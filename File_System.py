
class File:
    def __init__(self, filename, path):
        self.name = filename
        self.contents = []
        self.path = path

    def editline(self, line_number, new_content):
        if 0 < line_number <= len(self.contents):
            self.contents[line_number - 1] = new_content
        else:
            print("Invalid line number")

    def append(self, text):
        self.contents.append(text)

    def read(self):
        return ''.join(self.contents)

    def deline(self, line_number):
        if 0 < line_number <= len(self.contents):
            del self.contents[line_number - 1]
        else:
            print("Invalid line number")

    def rename(self, new_name):
        self.name = new_name

class Folder:
    def __init__(self,folder_name,path):
        self.name = folder_name
        self.children = dict()
        self.path = path

    def rename_folder(self, name):
        self.name = name

    def add_child(self, child):
        self.children[child.name] = child

    def remove_child(self, name):
        if name in self.children:
            del self.children[name]

    def get_child(self, name):
        return self.children.get(name)

    def list_children(self):
        return list(self.children.keys())

    def all_children(self):
        return list(self.children.values())

def Singleton(cls):
    instances={}
    def get_instance(*args,**kwargs):
        if cls not in instances:
            instances[cls]= cls (*args , **kwargs)
        return instances[cls]
    return get_instance

x = Folder('/','/')
@Singleton
class Unix:
    def __init__(self):
        self.root_folder = x
        self.current_folder = x

    @staticmethod
    def get_relative_path(obj1, obj2):
        for i in range(min(len(obj1.path), len(obj2.path))):
            if obj1.path[i] == obj2.path[i]:
                continue
            else:
                z = obj1.path[i:]
                y = obj2.path[i:]
                z.reverse()
                z.append(obj1.path[i - 1])
                z.extend(y)
                path_list = []
                for item in z:
                    path_list.append(item)
                return path_list

    def walk_through_a_path(self, path):
        if path.startswith('/'): # main_path
            parts = path.split('/') # paths' parts are separated by /
            current = self.root_folder
        else:
            parts = path.split('/') #relative_path
            current = self.current_folder #if cd was not used anywhere before, this is the same as root folder
        for part in parts:
            if part == '' or part == '.':
                continue
            elif part == '..':
                if current.name != '/':
                    current = self.get_parent(current)
            else:
                current = current.get_child(part)
                if current is None:
                    raise Exception(f"{part}: No such file or directory!")
        return current

    def reverse_forward_walk(self, path):
        if path.startswith('/'):
            return unix.walk_through_a_path(path)

        parts = path.split('/')  # relative_path
        current = self.current_folder
        for part in parts:
            if part == '':
                if self.get_parent(current) == x:
                    current = self.root_folder
            elif part in current.list_children():
                current = current.get_child(part)
                if current is None:
                    raise Exception(f"{part}: No such file or directory!")
            elif current.name != '/' :
                if part == self.get_parent(current).name :
                    current = self.get_parent(current)
        return current

    def get_parent(self, directory: Folder):
        list_of_path = [self.root_folder]
        while len(list_of_path) != 0:
            current = list_of_path.pop(-1)
            for item in current.all_children():
                if directory == item:
                    return current
                list_of_path.append(item)
                # saving all the children branches then checking their child branches one by one
        return None

    def ls(self, path ='.'):
        directory = self.walk_through_a_path(path)
        return directory.list_children()

    def rename_folder(self, path , name):
        folder1 = self.walk_through_a_path(path)
        if isinstance(folder1, Folder):
            folder1.rename_folder(name)
        else:
            raise Exception(f"{path} is a File!")

    def mv(self, source, destination):
        source_parts = source.split('/')
        destination_parts = destination.split('/')

        parent_of_source_path = '/'.join(source_parts[:-1])
        parent_of_destination_path = '/'.join(destination_parts[:-1])

        obj = self.walk_through_a_path(source)
        obj.path = destination
        parent_of_source = self.walk_through_a_path(parent_of_source_path)
        parent_of_source.remove_child(source_parts[-1])
        parent_of_destination = self.walk_through_a_path(parent_of_destination_path)
        parent_of_destination.add_child(obj)

    def cp_folder(self, source, destination):
        source_parts = source.split('/')
        destination_parts = destination.split('/')

        source_folder_name = source_parts[-1]
        source_parent_path = '/' + '/'.join(source_parts[:-1]) if len(source_parts) > 1 else '/'
        destination_parent_path = '/' + '/'.join(destination_parts[:-1]) if len(destination_parts) > 1 else '/'

        parent_of_source = self.walk_through_a_path(source_parent_path)
        obj_to_copy = parent_of_source.get_child(source_folder_name)
        destination_parent = self.walk_through_a_path(destination_parent_path)

        copied_folder = self.copying_folder(obj_to_copy, destination)
        destination_parent.add_child(copied_folder)

    def copying_folder(self, obj , path):
        def recursive_copy(original_folder, path_prefix):
                new_folder = Folder(original_folder.name, path_prefix)
                for child in original_folder.all_children():
                    if isinstance(child, File):
                        new_file = File(child.name, f'{path_prefix}/{child.name}')
                        new_file.contents = child.contents.copy()
                        new_folder.add_child(new_file)
                    elif isinstance(child, Folder):
                        child_copy = recursive_copy(child, f'{path_prefix}/{child.name}')
                        new_folder.add_child(child_copy)
                return new_folder
        return recursive_copy(obj, path)

    def cp_file(self, source, destination):
        source_parts = source.split('/')
        destination_parts = destination.split('/')

        source_file_name = source_parts[-1]
        source_parent_path = '/'.join(source_parts[:-1])
        destination_parent_path = '/'.join(destination_parts[:-1])

        source_parent_dir = self.walk_through_a_path(source_parent_path)
        file_obj = source_parent_dir.get_child(source_file_name)

        copied_file = File(file_obj.name,destination)
        copied_file.contents = file_obj.contents.copy() #for actually coping the content with no links to the source object

        destination_parent = self.walk_through_a_path(destination_parent_path)
        destination_parent.add_child(copied_file)

    def touch(self, path):
        parts = path.split('/')
        file_name = parts[-1]
        parent_path = '/'.join(parts[:-1]) or '/'
        parent_folder = self.walk_through_a_path(parent_path)
        new_file = File(file_name, path)
        parent_folder.add_child(new_file)

    def mkdir(self, path):
        parts = path.split('/')
        dir_name = parts[-1]
        parent_path = '/'.join(parts[:-1]) or '/'

        parent_dir = self.walk_through_a_path(parent_path)
        new_directory = Folder(dir_name,path)
        parent_dir.add_child(new_directory)

    def rm(self, path):
        parts = path.split('/')
        file_name = parts[-1]
        parent_path = '/'.join(parts[:-1]) or '/'

        parent_dir = self.walk_through_a_path(parent_path)
        parent_dir.remove_child(file_name)

    def cd(self, path):
        self.current_folder = self.walk_through_a_path(path)

    def editline(self, path, line_number, new_content):
        file = self.walk_through_a_path(path)
        if isinstance(file, File):
            file.editline(line_number, new_content)
        else:
            raise Exception(f"{path} is a directory")

    def deline(self, path, line_number):
        file = self.walk_through_a_path(path)
        if isinstance(file, File):
            file.deline(line_number)
        else:
            raise Exception(f"{path} is a directory")

    def append(self, path, text):
        file = self.walk_through_a_path(path)
        if isinstance(file, File):
            file.append(text)
        else:
            raise Exception(f"{path} is a directory")

    def rename(self, path, new_name):
        file = self.walk_through_a_path(path)
        if isinstance(file, File):
            file.rename(new_name)
        else:
            raise Exception(f"{path} is a directory")

    def cat(self, path):
        file = self.walk_through_a_path(path)
        if isinstance(file, File):
            return file.read()
        else:
            raise Exception(f"{path} is a directory")

def get_unix():
    return Unix()

def Unix_terminal():
    unix = Unix()
    print("Welcome to my mock Unix terminal!Type 'exit' to quit.")

    while True:
        try:
            command_input = input(f"{unix.current_folder.name}$ ").strip()
            if not command_input:
                continue
            if command_input.lower() == 'exit':
                break

            parts = command_input.split()
            command = parts[0]

            if command == 'ls':
                if len(parts) > 1:
                    path = parts[1]
                else :
                    path = '.'
                print('\n'.join(unix.ls(path)))

            elif command == 'cd':
                if len(parts) < 2:
                    print("cd: missing operand")
                else:
                    unix.cd(parts[1])

            elif command == 'mkdir':
                if len(parts) < 2:
                    print("mkdir: missing operand")
                else:
                    unix.mkdir(parts[1])

            elif command == 'touch':
                if len(parts) < 2:
                    print("touch: missing operand")
                else:
                    unix.touch(parts[1])

            elif command == 'cat':
                if len(parts) < 2:
                    print("cat: missing operand")
                else:
                    print(unix.cat(parts[1]))

            elif command == 'rm':
                if len(parts) < 2:
                    print("rm: missing operand")
                else:
                    unix.rm(parts[1])

            elif command == 'editline':
                if len(parts) < 3:
                    print("edit: usage: edit <file_path> <line_number>")
                else:
                    file_path = parts[1]
                    line_number = int(parts[2])
                    print("Enter new content.Finish with entering END//")
                    lines = []
                    while True:
                        line = input()
                        if line.strip() == "END//":
                            break
                        lines.append(line)
                    unix.editline(file_path, line_number, '\n'.join(lines) + '\n')

            elif command == 'deline':
                if len(parts) < 3:
                    print("deline: usage: deline <file_path> <line_number>")
                else:
                    file_path = parts[1]
                    line_number = int(parts[2])
                    unix.deline(file_path, line_number)

            elif command == 'rename':
                if len(parts) < 3:
                    print("rename: usage: rename <file_path> <new_name>")
                else:
                    file_path = parts[1]
                    new_name = parts[2]
                    unix.rename(file_path, new_name)

            elif command == 'append':
                if len(parts) < 2:
                    print("append: usage: append <file_path>")
                else:
                    file_path = parts[1]
                    print("Enter content to append. Finish with END//")
                    lines = []
                    while (True):
                        line = input()
                        if line.strip() == "END//":
                            break
                        lines.append(line)
                    unix.append(file_path, '\n'.join(lines) + '\n')

            elif command == 'mv':
                if len(parts) < 3:
                    print("mv: usage: mv <source_path> <destination_path>")
                else:
                    unix.mv(parts[1], parts[2])

            elif command == 'cp':
                if len(parts) < 3:
                    print("cp: usage: cp <source_path> <destination_path>")
                else:
                    unix.cp_file(parts[1], parts[2])

            elif command == 'cp_folder':
                if len(parts) < 3:
                    print("cp_folder: usage: cp_folder <source_path> <destination_path>")
                else:
                    unix.cp_folder(parts[1], parts[2])
                    
            elif command == 'relative_path':
                if len(parts) < 3:
                    print("relative_path: usage: relative_path <path_obj1> <path_obj2")
                else:
                    obj1 = unix.walk_through_a_path(parts[1])
                    obj2 = unix.walk_through_a_path(parts[2])
                    Unix.get_relative_path(obj1 , obj2)
            else:
                print(f"{command} :command not found")

        except Exception as e:
            print(f"Error: {e}")

unix = Unix()

# unix.mkdir('//Documents')
# unix.mkdir('//Documents/photos')
# unix.mkdir('//Downloads')
# unix.mkdir('//Downloads/movies')
# unix.mkdir('//Downloads/movies/first')
# unix.cd('//Downloads/movies')
# z= unix.reverse_forward_walk('first/movies/Downloads///Documents/photos')
# print(z.name)
