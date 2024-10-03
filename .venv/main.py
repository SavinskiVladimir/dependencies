import xml.etree.ElementTree as ET

def parse_dependencies(apk_file):
    dependencies = {}
    with open(apk_file, 'r') as file:
        for line in file:
            if line.startswith("depends:"):
                pkg_deps = line.split(":")[1].strip().split(",")
                dependencies[apk_file] = [dep.strip() for dep in pkg_deps]
    return dependencies

def get_transitive_dependencies(pkg, dependencies, visited=None):
    if visited is None:
        visited = set()
    if pkg in visited:
        return []
    visited.add(pkg)
    transitive_deps = []
    for dep in dependencies.get(pkg, []):
        transitive_deps.append(dep)
        transitive_deps.extend(get_transitive_dependencies(dep, dependencies, visited))
    return transitive_deps

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
        'visualizationPath': root.find('visualizationPath').text,
        'packagePath': root.find('packagePath').text,
        'outputPath': root.find('outputPath').text,
        'maxDepth': int(root.find('maxDepth').text)
    }
    return config


if __name__ == "__main__":
    config = read_config('configuration.xml')

    # парсинг зависимостей
    dependencies = parse_dependencies(config['packagePath'])

    # получение транзитивных зависимостей для каждого пакета
    all_transitive_deps = {}
    for pkg in dependencies.keys():
        all_transitive_deps[pkg] = get_transitive_dependencies(pkg, dependencies, max_depth=config['maxDepth'])

    # генерация PlantUML кода
    plantuml_code = generate_plantuml(all_transitive_deps)
    print(plantuml_code)

    # Сохранение PlantUML кода в файл
    with open(config['outputPath'], 'w') as f:
        f.write(plantuml_code)

    print("PlantUML code generated and saved to", config['outputPath'])