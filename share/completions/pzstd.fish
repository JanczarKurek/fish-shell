# Completions for pzstd

complete -c pzstd -s d -l decompress -d "Decompress" -x -a "
(
    __fish_complete_suffix .zst
)
"

complete -c pzstd -s t -l test -d "Test the integrity"

for level in (seq 1 19)
    complete -c pzstd -o $level -d "Set compression level"
end

complete -c pzstd -l ultra -d "Enable compression level beyond 19"

## If Python 3.4 or later installed, the number of physical cores is assigned to a variable.
set -l python (__fish_anypython)
set -q python[1]; and set -l physical_cores ($python -c 'import os; os.cpu_count() is not None and print(os.cpu_count())' 2> /dev/null)

if set -q physical_cores; and test -n "$physical_cores"
    complete -x -c pzstd -s p -l processes -a "(seq 1 $physical_cores)" -d "De/compress using $threads working threads"
else
    complete -x -c pzstd -s p -l processes -a NUM -d "De/compress using NUM working threads"
end

complete -r -c pzstd -s o -d "Specify file to save"
complete -c pzstd -s f -l force -d "Overwrite without prompting"
complete -c pzstd -s c -l stdout -d "Force write to stdout"
complete -c pzstd -l rm -d "Remove input file(s) after de/compression"
complete -c pzstd -s k -l keep -d "Keep input file(s) (default)"
complete -c pzstd -s r -d "Recurse directories"
complete -c pzstd -s h -l help -d "Show help"
complete -c pzstd -s H -d "Show long help"
complete -c pzstd -s V -l version -d "Show version"
complete -c pzstd -s v -l verbose -d "Be verbose"
complete -c pzstd -s q -l quiet -d "Suppress warnings"
complete -c pzstd -l no-check -d "Disable integrity check"