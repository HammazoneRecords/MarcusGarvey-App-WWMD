# tools/solob.ps1
# DEPRECATED: This tool has been replaced by the Python CLI 'mw'.

Write-Warning "solob.ps1 is deprecated."
Write-Warning "Please use the Python wrapper 'mw' instead."
Write-Warning "Usage: python tools/cli/mw.py <command>"
Write-Warning "Examples:"
Write-Warning "  python tools/cli/mw.py state"
Write-Warning "  python tools/cli/mw.py observe --note '...'"
Write-Warning "  python tools/cli/mw.py record --note '...'"
Write-Warning "  python tools/cli/mw.py run --intent '...' --script <path> -- [args]"

exit 1
