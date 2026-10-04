import os
import re

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # 1. Replace @Observable with ObservableObject inheritance
    # Matches: @Observable\nfinal class Name {
    # Replace: final class Name: ObservableObject {
    if '@Observable' in content:
        content = content.replace('@Observable\n', '')
        content = re.sub(r'(final\s+class\s+\w+)(\s*\{)', r'\1: ObservableObject\2', content)
        content = re.sub(r'(class\s+\w+)(\s*\{)', r'\1: ObservableObject\2', content)

        # Add @Published to properties that are not computed and not private/let? 
        # Actually it's safer to just add @Published to `var` that are state.
        # Let's find properties like `var showPower: Bool { didSet }` -> `@Published var showPower`
        # This is a bit tricky, let's just add @Published to variables.
        # A simple hack: replace `    var ` with `    @Published var `, EXCEPT if it's computed.
        # It's better to manually replace in the 3 known files.

    # 2. @Environment(PowerMonitor.self) -> @EnvironmentObject
    content = re.sub(
        r'@Environment\(\s*(\w+)\.self\s*\)\s*(?:private\s+)?var\s+(\w+)', 
        r'@EnvironmentObject private var \2: \1', 
        content
    )
    
    # 3. .environment(monitor) -> .environmentObject(monitor)
    # Be careful not to replace .environment(\.colorScheme, .dark)
    content = re.sub(r'\.environment\(\s*([a-zA-Z0-9_]+)\s*\)', r'.environmentObject(\1)', content)

    # 4. @Bindable var monitor = monitor -> removed or just rely on EnvironmentObject
    content = re.sub(r'@Bindable\s+var\s+\w+\s*=\s*\w+', '', content)

    # 5. onChange(of: ..., initial: true)
    content = content.replace('initial: true', '') # simplistic, might leave extra commas.
    # .onChange(of: scenePhase, initial: true) { _, phase in
    content = re.sub(
        r'\.onChange\(\s*of:\s*([^,]+),\s*initial:\s*true\s*\)\s*\{\s*[^,]+,\s*([^ ]+)\s+in', 
        r'.onChange(of: \1) { \2 in', 
        content
    )

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Modified: {file_path}")

def main():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.swift'):
                process_file(os.path.join(root, file))

if __name__ == '__main__':
    main()
