"""
aslrcheck.py - Plugin Volatility 3: comprobación de ASLR en procesos Windows
===============================================================================
Itera todos los procesos de un volcado de memoria Windows, extrae el PE
de cada uno y verifica si tiene ASLR activo comprobando:
  - IMAGE_DLL_CHARACTERISTICS_DYNAMIC_BASE (0x0040) en DllCharacteristics
  - IMAGE_FILE_RELOCS_STRIPPED (0x0001) en FileHeader.Characteristics

ERRORES CORREGIDOS:
    1. `requirements.SymboltableRequirement` → `requirements.SymbolTableRequirement`
       (mayúscula en 'T' de Table).
    2. `element_type = init` → `element_type = int`
       (`init` no es un tipo; se necesita el tipo Python `int`).
    3. `proc.ImageFIleName` → `proc.ImageFileName`
       (typo: 'FIle' → 'File'; la 'l' estaba en mayúscula por error).

REQUISITOS:
    pip install volatility3 pefile
    Ejecutar como plugin dentro del framework Volatility 3.

EJEMPLOS DE EJECUCIÓN:
    # Listar procesos sin ASLR en un dump de memoria:
    vol -f memoria.dmp windows.aslrcheck.AslrCheck

    # Filtrar por PID específico:
    vol -f memoria.dmp windows.aslrcheck.AslrCheck --pid 1234
"""

import io
import logging
import os
import pefile

from typing import Callable, List

from volatility3.framework import constants, exceptions, interfaces, renderers
from volatility3.framework.configuration import requirements
from volatility3.framework.renderers import format_hints
from volatility3.framework.symbols import intermed
from volatility3.framework.symbols.windows import extensions
from volatility3.plugins.windows import pslist

vollog = logging.getLogger(__name__)

# Constantes de cabecera PE para la comprobación de ASLR
IMAGE_DLL_CHARACTERISTICS_DYNAMIC_BASE = 0x0040
IMAGE_FILE_RELOCS_STRIPPED              = 0x0001


def check_aslr(pe: pefile.PE) -> bool:
    """
    Determina si un PE tiene ASLR correctamente activado.

    Un PE tiene ASLR si:
      - DllCharacteristics incluye DYNAMIC_BASE, Y
      - FileHeader.Characteristics NO incluye RELOCS_STRIPPED.

    Args:
        pe (pefile.PE): Objeto PE ya cargado.
    Returns:
        bool: True si ASLR está activo, False en caso contrario.
    """
    pe.parse_data_directories(
        [pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG']]
    )
    dynamic = bool(pe.OPTIONAL_HEADER.DllCharacteristics & IMAGE_DLL_CHARACTERISTICS_DYNAMIC_BASE)
    stripped = bool(pe.FILE_HEADER.Characteristics & IMAGE_FILE_RELOCS_STRIPPED)

    return dynamic and not stripped


class AslrCheck(interfaces.plugins.PluginInterface):
    """Plugin de Volatility 3 que lista procesos y su estado de ASLR."""

    @classmethod
    def get_requirements(cls):
        return [
            requirements.TranslationLayerRequirement(
                name='primary',
                description='Memory Layer for the kernel',
                architectures=["Intel32", "Intel64"]
            ),
            # FIX: era 'SymboltableRequirement' → 'SymbolTableRequirement'
            requirements.SymbolTableRequirement(
                name="nt_symbols",
                description="Windows Kernel symbols"
            ),
            requirements.PluginRequirement(
                name='pslist',
                plugin=pslist.PsList,
                version=(1, 0, 0)
            ),
            requirements.ListRequirement(
                name='pid',
                # FIX: era 'element_type = init' → 'element_type = int'
                element_type=int,
                description="Process IDs to include (all others excluded)",
                optional=True
            ),
        ]

    @classmethod
    def create_pid_filter(cls, pid_list: List[int] = None) -> Callable[[interfaces.objects.ObjectInterface], bool]:
        """Devuelve una función que filtra procesos por PID."""
        filter_func = lambda _: False
        pid_list = pid_list or []
        filter_list = [x for x in pid_list if x is not None]
        if filter_list:
            filter_func = lambda x: x.UniqueProcessId not in filter_list
        return filter_func

    def _generator(self, procs):
        pe_table_name = intermed.IntermediateSymbolTable.create(
            self.context,
            self.config_path,
            "windows",
            "pe",
            class_types=extensions.pe.class_types
        )
        procnames = []

        for proc in procs:
            # FIX: era 'proc.ImageFIleName' → 'proc.ImageFileName'
            procname = proc.ImageFileName.cast(
                "string",
                max_length=proc.ImageFileName.vol.count,
                errors='replace'
            )
            if procname in procnames:
                continue
            procnames.append(procname)

            proc_id = "Unknown"
            try:
                proc_id = proc.UniqueProcessId
                proc_layer_name = proc.add_process_layer()
            except exceptions.InvalidAddressException as e:
                vollog.error(f"Process {proc_id}: invalid address {e} in layer {e.layer_name}")
                continue

            peb = self.context.object(
                self.config['nt_symbols'] + constants.BANG + "_PEB",
                layer_name=proc_layer_name,
                offset=proc.Peb
            )

            try:
                dos_header = self.context.object(
                    pe_table_name + constants.BANG + "_IMAGE_DOS_HEADER",
                    offset=peb.ImageBaseAddress,
                    layer_name=proc_layer_name
                )
            except Exception:
                continue

            pe_data = io.BytesIO()
            for offset, data in dos_header.reconstruct():
                pe_data.seek(offset)
                pe_data.write(data)
            pe_data_raw = pe_data.getvalue()
            pe_data.close()

            try:
                pe = pefile.PE(data=pe_data_raw)
            except Exception:
                continue

            aslr = check_aslr(pe)
            yield (0, (proc_id, procname, format_hints.Hex(pe.OPTIONAL_HEADER.ImageBase), aslr))

    def run(self):
        procs = pslist.PsList.list_processes(
            self.context,
            self.config["primary"],
            self.config["nt_symbols"],
            filter_func=self.create_pid_filter(self.config.get('pid', None))
        )
        return renderers.TreeGrid(
            [
                ("PID",      int),
                ("Filename", str),
                ("Base",     format_hints.Hex),
                ("ASLR",     bool),
            ],
            self._generator(procs)
        )
