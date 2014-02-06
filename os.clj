(import 'os)


; Get the current working directory
(def cwd (. os getcwd))


; Get a list of the filenames in the current directory
(def ls (fn* [] (. os (listdir (cwd)))))