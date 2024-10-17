import xml.etree.ElementTree as ET

def parse_dependencies(apk_file):
    dependencies = {} # словарь для хранения полученных зависимостей
    with open(apk_file, 'r') as file:
        current_pkg = None
        in_multiline = False # флаг, показывающий, что обрабатываемый объект имеет несколько построчно записанных зависимостей
        temp_deps = "" # строка для хранения построчно записанных зависимостей
        for line in file:
            line = line.strip()
            if line.startswith("pkgname="): # получение имени очередного пакета
                current_pkg = line.split("=")[1].strip()
                dependencies[current_pkg] = [] # добавление в словарь пары: пакет - список его зависимостей
            elif line.startswith("depends="): # обработка зависимостей
                if '"' in line: # если строка содержит " - значит зависимостей несколько и они записаны построчно
                    in_multiline = True
                    temp_deps += line.split("=")[1].strip().strip('"') # добавление зависимости из первой строки
                else:
                    temp_deps += line.split("=")[1].strip() # добавление единственной зависимости
            elif line.startswith("makedepends="): # обработка зависимостей сборки
                if '"' in line:
                    in_multiline = True
                    temp_deps += line.split("=")[1].strip().strip('"')
                else:
                    temp_deps += line.split("=")[1].strip()
            elif in_multiline: # если идёт обработка построчных зависимостей
                temp_deps += " " + line.strip() # добавление очередной зависимости
                if line.endswith('"'): # окончанием перечисления служит символ "
                    in_multiline = False
                    if current_pkg:
                        # добавление в список всех зависимостей зависимостей для текущего пакета
                        dependencies[current_pkg].extend(temp_deps[:-1].strip().split())
                        temp_deps = ""
            elif not in_multiline and temp_deps != "": # если была только одна зависимость
                dependencies[current_pkg].extend(temp_deps)
                temp_deps = ""

    return dependencies


# def get_transitive_dependencies(pkg, dependencies, visited=None):
#     if visited is None:
#         visited = set()
#     if pkg in visited:
#         return []
#     visited.add(pkg)
#     transitive_deps = []
#     for dep in dependencies.get(pkg, []):
#         transitive_deps.append(dep)
#         transitive_deps.extend(get_transitive_dependencies(dep, dependencies, visited))
#     return transitive_deps

def generate_plantuml(dependencies):
    plantuml_code = "@startuml\n"
    for pkg, deps in dependencies.items():
        for dep in deps:
            plantuml_code += f"{pkg} --> {dep}\n"
    plantuml_code += "@enduml"
    return plantuml_code

def read_config(config_file):
    tree = ET.parse(config_file)
    root = tree.getroot()
    config = {
        'packagePath': root.find('packagePath').text,
        'outputPath': root.find('outputPath').text,
        'maxDepth': int(root.find('maxDepth').text)
    }
    return config


if __name__ == "__main__":
    config = read_config('D:\дз\конф_управление\dependecies\.venv\configuration.xml')

    # парсинг зависимостей
    dependencies = parse_dependencies(config['packagePath'])

    # получение транзитивных зависимостей для каждого пакета
    # all_transitive_deps = {}
    # for pkg in dependencies.keys():
    #     all_transitive_deps[pkg] = get_transitive_dependencies(pkg, dependencies)

    # генерация PlantUML кода
    plantuml_code = generate_plantuml(dependencies)
    print(plantuml_code)

    # сохранение PlantUML кода в файл
    with open(config['outputPath'], 'w') as f:
        f.write(plantuml_code)