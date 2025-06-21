import os
import re

def find_files(directory):
    """Find all files in the specified directory and subdirectories"""
    found_files = []
    
    exclude_file_patterns = [
        'mask_secrets.py',
        '*_masked.*',
        '*.pyc',
        'create_sample_app.py',
        'README.md',
        'LICENSE',
        '.gitignore'
    ]
    
    exclude_dir_patterns = [
        '__pycache__',
        '.git',
        '.vscode',
        '.idea',
        'node_modules',
        'venv',
        'env',
        'dist',
        'build',
        'target',
        'vendor',
        '.next',
        '.nuxt',
        'coverage',
        '.pytest_cache',
        '.mypy_cache',
        'logs',
        'tmp',
        'temp'
    ]
    
    def should_exclude_directory(dir_name, dir_path):
        for pattern in exclude_dir_patterns:
            if pattern.startswith('*') and pattern.endswith('*'):
                if pattern[1:-1] in dir_name:
                    return True
            elif pattern.startswith('*'):
                if dir_name.endswith(pattern[1:]):
                    return True
            elif pattern.endswith('*'):
                if dir_name.startswith(pattern[:-1]):
                    return True
            elif dir_name == pattern:
                return True
        return False
    
    def should_exclude_file(file_name, file_path):
        for pattern in exclude_file_patterns:
            if pattern.startswith('*') and pattern.endswith('*'):
                if '_masked.' in file_name:
                    return True
            elif pattern.startswith('*.'):
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern.startswith('*'):
                if file_name.endswith(pattern[1:]):
                    return True
            elif pattern.endswith('*'):
                if file_name.startswith(pattern[:-1]):
                    return True
            elif file_name == pattern:
                return True
        return False
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not should_exclude_directory(d, os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            if not should_exclude_file(file, file_path):
                found_files.append(file_path)
    
    return found_files

def read_file_content(file_path):
    """Read file content with encoding handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='shift_jis') as file:
                return file.read()
        except:
            return None
    except Exception:
        return None

def create_secret_patterns():
    """Create regex patterns for detecting sensitive information"""
    patterns = []
    
    general_key_patterns = [
        r'(password\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(pass\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(pwd\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(token\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(auth[_\-]?token\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(access[_\-]?token\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(session[_\-]?token\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(secret\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(secret[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(secret[_\-]?key[_\-]?base\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(client[_\-]?secret\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(app[_\-]?secret\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(api[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(access[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(private[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(public[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(encryption[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(consumer[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(consumer[_\-]?secret\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(client[_\-]?id\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(app[_\-]?id\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(webhook[_\-]?secret\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(jwt[_\-]?secret\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(session[_\-]?secret\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(account[_\-]?sid\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(publishable[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(passphrase\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
    ]
    
    define_patterns = [
        r"(define\s*\(\s*['\"]DB_PASS['\"],\s*['\"])([^'\"]+)(['\"])",
        r"(define\s*\(\s*['\"].*(?:PASS|PASSWORD|SECRET|KEY|TOKEN)['\"],\s*['\"])([^'\"]+)(['\"])",
        r"(const\s+\w*(?:PASSWORD|SECRET|KEY|TOKEN|API)\w*\s*=\s*['\"])([^'\"]+)(['\"])",
        r"(\w*(?:PASSWORD|SECRET|KEY|TOKEN|API)\w*\s*=\s*['\"])([^'\"]+)(['\"])",
    ]
    
    env_patterns = [
        r'^(\w*(?:PASSWORD|SECRET|KEY|TOKEN|API|SID)\w*\s*=\s*)([^\s#]+)',
        r'^(DATABASE_URL\s*=\s*[^:]+://[^:]+:)([^@]+)(@.*)',
        r'^(REDIS_URL\s*=\s*[^:]+://[^:]*:)([^@]+)(@.*)',
    ]
    
    array_patterns = [
        r"(['\"](?:\w*(?:password|secret|key|token|api|pass|pwd)\w*)['\"][\s]*=>[\s]*['\"])([^'\"]+)(['\"])",
        r"(['\"](?:\w*(?:password|secret|key|token|api|pass|pwd)\w*)['\"][\s]*:[\s]*['\"])([^'\"]+)(['\"])",
    ]
    
    header_patterns = [
        r"(['\"]Authorization['\"][\s]*:[\s]*['\"]Bearer\s+)([^'\"]+)(['\"])",
        r"(['\"]X-API-Key['\"][\s]*:[\s]*['\"])([^'\"]+)(['\"])",
        r"('Authorization':\s*'Bearer\s+)([^']+)(')",
        r"(\"Authorization\":\s*\"Bearer\s+)([^\"]+)(\")",
    ]
    
    aws_patterns = [
        r'(AKIA[0-9A-Z]{16})',
        r'([A-Za-z0-9/+=]{40})',
        r'(AQoE[A-Za-z0-9/+=]+)',
    ]
    
    service_patterns = [
        r'(sk_(?:test|live)_[0-9A-Za-z]{24,})',
        r'(pk_(?:test|live)_[0-9A-Za-z]{24,})',
        r'(whsec_[0-9A-Za-z]{24,})',
        r'(SG\.[0-9A-Za-z_\-]{22}\.[0-9A-Za-z_\-]{43})',
        r'(ghp_[0-9A-Za-z]{36})',
        r'(GOCSPX-[0-9A-Za-z_\-]{28})',
        r'(AC[0-9a-f]{32})',
        r'(SK[0-9a-f]{32})',
        r'(key-[0-9a-f]{32})',
        r'(EAA[0-9A-Za-z]+)',
    ]
    
    jwt_patterns = [
        r'(eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*)',
    ]
    
    comment_patterns = [
        r'(#\s*\w*(?:PASSWORD|SECRET|KEY|TOKEN|API|SID)\w*\s*=\s*)([^\s#]+)',
    ]
    
    patterns.extend(general_key_patterns)
    patterns.extend(define_patterns)
    patterns.extend(env_patterns)
    patterns.extend(array_patterns)
    patterns.extend(header_patterns)
    patterns.extend(aws_patterns)
    patterns.extend(service_patterns)
    patterns.extend(jwt_patterns)
    patterns.extend(comment_patterns)
    
    return patterns

def find_secrets_in_text(text, patterns):
    """Find sensitive information in text"""
    found_secrets = []
    
    for pattern in patterns:
        flags = re.IGNORECASE
        if any(service_pattern in pattern for service_pattern in ['AKIA', 'sk_', 'pk_', 'SG\.', 'ghp_', 'GOCSPX', 'AC[0-9a-f]', 'SK[0-9a-f]', 'key-[0-9a-f]', 'EAA', 'eyJ']):
            flags = 0
        
        matches = re.finditer(pattern, text, flags)
        
        for match in matches:
            secret_info = {
                'pattern': pattern,
                'full_match': match.group(0),
                'start': match.start(),
                'end': match.end(),
                'groups': match.groups()
            }
            found_secrets.append(secret_info)
    
    return found_secrets

def mask_secrets_in_text(text, patterns):
    """Mask sensitive information in text"""
    masked_text = text
    
    for pattern in patterns:
        flags = re.IGNORECASE
        if any(service_pattern in pattern for service_pattern in ['AKIA', 'sk_', 'pk_', 'SG\.', 'ghp_', 'GOCSPX', 'AC[0-9a-f]', 'SK[0-9a-f]', 'key-[0-9a-f]', 'EAA', 'eyJ']):
            flags = 0
        
        def replace_secret(match):
            groups = match.groups()
            
            if len(groups) == 1:
                return "***MASKED***"
            elif len(groups) == 3 and ('DATABASE_URL' in match.group(0) or 'REDIS_URL' in match.group(0)):
                prefix = groups[0]
                suffix = groups[2]
                return prefix + "***" + suffix
            elif len(groups) == 3:
                prefix = groups[0]
                suffix = groups[2]
                return prefix + "***" + suffix
            elif len(groups) == 2:
                prefix = groups[0]
                return prefix + "***"
            else:
                return "***MASKED***"
        
        masked_text = re.sub(pattern, replace_secret, masked_text, flags=flags)
    
    return masked_text

def overwrite_file(file_path, masked_content):
    """Overwrite existing file with masked content"""
    try:
        backup_path = file_path + '.backup'
        
        with open(file_path, 'r', encoding='utf-8') as original:
            original_content = original.read()
        
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original_content)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(masked_content)
        
        return backup_path
    except Exception:
        return None

def cleanup_backups(current_dir):
    """Clean up backup files"""
    backup_files = []
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.endswith('.backup'):
                backup_files.append(os.path.join(root, file))
    
    if backup_files:
        print(f"\nFound {len(backup_files)} backup files")
        
        while True:
            cleanup = input("Delete backup files? (y/n): ").lower().strip()
            if cleanup in ['y', 'yes']:
                for backup_file in backup_files:
                    try:
                        os.remove(backup_file)
                    except Exception:
                        pass
                print("Backup files deleted")
                break
            elif cleanup in ['n', 'no']:
                print("Backup files kept")
                break

def main():
    print("Secret Masking Tool")
    print("=" * 30)
    
    current_dir = os.getcwd()
    print(f"Working directory: {current_dir}")
    
    print("\nWarning: This tool will overwrite existing files.")
    print("Backup files (.backup) will be created for safety.")
    
    while True:
        confirm = input("\nContinue? (y/n): ").lower().strip()
        if confirm in ['y', 'yes']:
            break
        elif confirm in ['n', 'no']:
            print("Cancelled")
            return
        else:
            print("Please enter 'y' or 'n'")
    
    patterns = create_secret_patterns()
    print(f"\nDetection patterns: {len(patterns)}")
    
    print("Scanning files...")
    files = find_files(current_dir)
    print(f"Target files: {len(files)}")
    
    total_secrets_found = 0
    files_with_secrets = 0
    files_overwritten = 0
    backup_files_created = 0
    
    print("\nProcessing files...")
    print("-" * 30)
    
    for file_path in files:
        print(f"\n{os.path.relpath(file_path, current_dir)}")
        content = read_file_content(file_path)
        
        if content is not None:
            secrets = find_secrets_in_text(content, patterns)
            
            if secrets:
                print(f"  Found {len(secrets)} secrets")
                
                total_secrets_found += len(secrets)
                files_with_secrets += 1
                
                print("  Masking...")
                masked_content = mask_secrets_in_text(content, patterns)
                
                backup_path = overwrite_file(file_path, masked_content)
                if backup_path:
                    files_overwritten += 1
                    backup_files_created += 1
                    print("  Completed")
                
            else:
                print("  No secrets found")
        else:
            print("  Skipped (unreadable)")
    
    print("\n" + "=" * 30)
    print("Results")
    print("=" * 30)
    print(f"Target files: {len(files)}")
    print(f"Files with secrets: {files_with_secrets}")
    print(f"Total secrets found: {total_secrets_found}")
    print(f"Files overwritten: {files_overwritten}")
    print(f"Backup files created: {backup_files_created}")
    
    if backup_files_created > 0:
        print(f"\nOriginal files saved with .backup extension")
        cleanup_backups(current_dir)
    
    print("\nCompleted!")

if __name__ == "__main__":
    main()
