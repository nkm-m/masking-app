import os
import re

def find_files(directory):
    """指定されたディレクトリ配下のすべてのファイルを検索する"""
    found_files = []
    
    # 除外するファイルのパターン
    exclude_patterns = [
        'mask_secrets.py',  # 自分自身を除外
        '*_masked.*',       # 既にマスキング済みのファイルを除外
        '*.pyc',           # Pythonコンパイル済みファイルを除外
        '__pycache__',     # Pythonキャッシュディレクトリを除外
        'create_sample_app.py'  # サンプル生成スクリプトを除外
    ]
    
    for root, dirs, files in os.walk(directory):
        # __pycache__ ディレクトリを除外
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # 除外パターンをチェック
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.startswith('*') and pattern.endswith('*'):
                    # *_masked.* のようなパターン
                    if '_masked.' in file:
                        should_exclude = True
                        break
                elif pattern.startswith('*.'):
                    # *.pyc のようなパターン
                    if file.endswith(pattern[1:]):
                        should_exclude = True
                        break
                elif file == pattern:
                    # 完全一致
                    should_exclude = True
                    break
            
            if not should_exclude:
                found_files.append(file_path)
    
    return found_files

def read_file_content(file_path):
    """ファイルの内容を読み込む"""
    try:
        # テキストファイルとして読み込み（UTF-8エンコーディング）
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except UnicodeDecodeError:
        # UTF-8で読めない場合は、別のエンコーディングを試す
        try:
            with open(file_path, 'r', encoding='shift_jis') as file:
                content = file.read()
                return content
        except:
            print(f"  警告: {file_path} は読み込めませんでした（バイナリファイルの可能性）")
            return None
    except Exception as e:
        print(f"  エラー: {file_path} の読み込み中にエラーが発生しました: {e}")
        return None

def create_secret_patterns():
    """機密情報を検出するための正規表現パターンを作成"""
    patterns = []
    
    # 1. 一般的なキー:値のパターン（様々な形式に対応）
    general_key_patterns = [
        # password系
        r'(password\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(pass\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(pwd\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        
        # token系
        r'(token\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(auth[_\-]?token\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(access[_\-]?token\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(session[_\-]?token\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        
        # secret系
        r'(secret\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(secret[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(client[_\-]?secret\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(app[_\-]?secret\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(secret[_\-]?key[_\-]?base\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        
        # key系
        r'(api[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(access[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(private[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(public[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        r'(encryption[_\-]?key\s*[:=>\-]\s*["\']?)([^"\';\s,})\]]+)(["\']?)',
        
        # その他の機密情報
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
    
    # 2. 定数定義パターン（PHP, Python, JavaScript）
    define_patterns = [
        r"(define\s*\(\s*['\"]DB_PASS['\"],\s*['\"])([^'\"]+)(['\"])",
        r"(define\s*\(\s*['\"].*(?:PASS|PASSWORD|SECRET|KEY|TOKEN)['\"],\s*['\"])([^'\"]+)(['\"])",
        r"(const\s+\w*(?:PASSWORD|SECRET|KEY|TOKEN|API)\w*\s*=\s*['\"])([^'\"]+)(['\"])",
        r"(\w*(?:PASSWORD|SECRET|KEY|TOKEN|API)\w*\s*=\s*['\"])([^'\"]+)(['\"])",
    ]
    
    # 3. 環境変数パターン（.env ファイル）
    env_patterns = [
        r'^(\w*(?:PASSWORD|SECRET|KEY|TOKEN|API|SID)\w*\s*=\s*)([^\s#]+)',
        r'^(DATABASE_URL\s*=\s*[^:]+://[^:]+:)([^@]+)(@.*)',
        r'^(REDIS_URL\s*=\s*[^:]+://[^:]*:)([^@]+)(@.*)',
    ]
    
    # 4. 辞書・配列パターン（PHP, Python, JavaScript）
    array_patterns = [
        r"(['\"](?:\w*(?:password|secret|key|token|api|pass|pwd)\w*)['\"][\s]*=>[\s]*['\"])([^'\"]+)(['\"])",
        r"(['\"](?:\w*(?:password|secret|key|token|api|pass|pwd)\w*)['\"][\s]*:[\s]*['\"])([^'\"]+)(['\"])",
    ]
    
    # 5. HTTPヘッダーパターン
    header_patterns = [
        r"(['\"]Authorization['\"][\s]*:[\s]*['\"]Bearer\s+)([^'\"]+)(['\"])",
        r"(['\"]X-API-Key['\"][\s]*:[\s]*['\"])([^'\"]+)(['\"])",
        r"('Authorization':\s*'Bearer\s+)([^']+)(')",
        r"(\"Authorization\":\s*\"Bearer\s+)([^\"]+)(\")",
    ]
    
    # 6. AWS関連のパターン
    aws_patterns = [
        r'(AKIA[0-9A-Z]{16})',  # AWS Access Key ID
        r'([A-Za-z0-9/+=]{40})',  # AWS Secret Access Key (40文字)
        r'(AQoE[A-Za-z0-9/+=]+)',  # AWS Session Token
    ]
    
    # 7. 特定のサービスのAPIキーパターン
    service_patterns = [
        r'(sk_(?:test|live)_[0-9A-Za-z]{24,})',  # Stripe Secret Key
        r'(pk_(?:test|live)_[0-9A-Za-z]{24,})',  # Stripe Publishable Key
        r'(whsec_[0-9A-Za-z]{24,})',  # Stripe Webhook Secret
        r'(SG\.[0-9A-Za-z_\-]{22}\.[0-9A-Za-z_\-]{43})',  # SendGrid API Key
        r'(ghp_[0-9A-Za-z]{36})',  # GitHub Personal Access Token
        r'(GOCSPX-[0-9A-Za-z_\-]{28})',  # Google OAuth Client Secret
        r'(AC[0-9a-f]{32})',  # Twilio Account SID
        r'(SK[0-9a-f]{32})',  # Twilio API Key
        r'(key-[0-9a-f]{32})',  # Mailgun API Key
        r'(EAA[0-9A-Za-z]+)',  # Facebook Access Token
    ]
    
    # 8. JWTトークンパターン
    jwt_patterns = [
        r'(eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*)',  # JWT Token
    ]
    
    # 9. コメント内のパターン（# で始まるコメント）
    comment_patterns = [
        r'(#\s*\w*(?:PASSWORD|SECRET|KEY|TOKEN|API|SID)\w*\s*=\s*)([^\s#]+)',
    ]
    
    # すべてのパターンをまとめる
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
    """テキスト内の機密情報を検出する"""
    found_secrets = []
    
    for pattern in patterns:
        # 大文字小文字を区別しない検索（ただし、一部のパターンは除く）
        flags = re.IGNORECASE
        if any(service_pattern in pattern for service_pattern in ['AKIA', 'sk_', 'pk_', 'SG\.', 'ghp_', 'GOCSPX', 'AC[0-9a-f]', 'SK[0-9a-f]', 'key-[0-9a-f]', 'EAA', 'eyJ']):
            flags = 0  # サービス固有のパターンは大文字小文字を区別
        
        matches = re.finditer(pattern, text, flags)
        
        for match in matches:
            # マッチした情報を保存
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
    """テキスト内の機密情報をマスキングする"""
    masked_text = text
    
    # 各パターンでマスキングを実行
    for pattern in patterns:
        # 大文字小文字を区別しない検索（ただし、一部のパターンは除く）
        flags = re.IGNORECASE
        if any(service_pattern in pattern for service_pattern in ['AKIA', 'sk_', 'pk_', 'SG\.', 'ghp_', 'GOCSPX', 'AC[0-9a-f]', 'SK[0-9a-f]', 'key-[0-9a-f]', 'EAA', 'eyJ']):
            flags = 0  # サービス固有のパターンは大文字小文字を区別
        
        def replace_secret(match):
            groups = match.groups()
            
            # AWS Access Key、サービス固有のトークンなど（グループが1つだけ）
            if len(groups) == 1:
                return "***MASKED***"
            
            # 環境変数の特殊パターン（DATABASE_URL, REDIS_URL）
            elif len(groups) == 3 and ('DATABASE_URL' in match.group(0) or 'REDIS_URL' in match.group(0)):
                prefix = groups[0]  # "DATABASE_URL=postgresql://user:"
                password = groups[1]  # パスワード部分
                suffix = groups[2]   # "@host:port/db"
                return prefix + "***" + suffix
            
            # 一般的なキー:値の場合（グループが3つ）
            elif len(groups) == 3:
                prefix = groups[0]  # "password: " の部分
                value = groups[1]   # 実際の値
                suffix = groups[2]  # 引用符など
                
                # 値の部分だけをマスキング
                return prefix + "***" + suffix
            
            # コメント内のパターン（グループが2つ）
            elif len(groups) == 2:
                prefix = groups[0]  # "# API_KEY="
                value = groups[1]   # 実際の値
                return prefix + "***"
            
            # その他の場合
            else:
                return "***MASKED***"
        
        # 大文字小文字を区別しない置換
        masked_text = re.sub(pattern, replace_secret, masked_text, flags=flags)
    
    return masked_text

def overwrite_file(file_path, masked_content):
    """マスキングされた内容で既存ファイルを上書きする"""
    try:
        # バックアップファイルを作成（安全のため）
        backup_path = file_path + '.backup'
        
        # 元のファイルをバックアップ
        with open(file_path, 'r', encoding='utf-8') as original:
            original_content = original.read()
        
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original_content)
        
        # 元のファイルをマスキング版で上書き
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(masked_content)
        
        return backup_path
    except Exception as e:
        print(f"  エラー: ファイルの上書きに失敗しました: {e}")
        return None

def main():
    print("=" * 50)
    print("機密情報マスキングツール（上書き版）")
    print("=" * 50)
    
    current_dir = os.getcwd()
    print(f"作業ディレクトリ: {current_dir}")
    
    # 確認メッセージ
    print("\n⚠️  注意: このツールは既存ファイルを直接上書きします。")
    print("   安全のため、各ファイルのバックアップ（.backup）を作成します。")
    
    # ユーザーに確認を求める
    while True:
        confirm = input("\n続行しますか？ (y/n): ").lower().strip()
        if confirm in ['y', 'yes']:
            break
        elif confirm in ['n', 'no']:
            print("処理を中止しました。")
            return
        else:
            print("'y' または 'n' で回答してください。")
    
    # 機密情報検出パターンを作成
    patterns = create_secret_patterns()
    print(f"\n検出パターン数: {len(patterns)}")
    
    # ファイルを検索
    print("\nファイルを検索しています...")
    files = find_files(current_dir)
    print(f"処理対象ファイル数: {len(files)}")
    
    # 統計用の変数
    total_secrets_found = 0
    files_with_secrets = 0
    files_overwritten = 0
    backup_files_created = 0
    
    # 各ファイルで機密情報を検索・マスキング
    print("\n機密情報を検索・マスキングしています...")
    print("-" * 50)
    
    for file_path in files:
        print(f"\n📁 {os.path.relpath(file_path, current_dir)}")
        content = read_file_content(file_path)
        
        if content is not None:
            secrets = find_secrets_in_text(content, patterns)
            
            if secrets:
                print(f"  ⚠️  機密情報が {len(secrets)} 件見つかりました:")
                for i, secret in enumerate(secrets, 1):
                    print(f"    {i}. '{secret['full_match']}'")
                
                # 統計を更新
                total_secrets_found += len(secrets)
                files_with_secrets += 1
                
                # マスキングを実行
                print("  🔒 マスキングを実行しています...")
                masked_content = mask_secrets_in_text(content, patterns)
                
                # 既存ファイルを上書き
                backup_path = overwrite_file(file_path, masked_content)
                if backup_path:
                    files_overwritten += 1
                    backup_files_created += 1
                    relative_backup_path = os.path.relpath(backup_path, current_dir)
                    print(f"  💾 バックアップ作成: {relative_backup_path}")
                    print(f"  ✅ ファイル上書き完了")
                
            else:
                print("  ✅ 機密情報は見つかりませんでした")
        else:
            print("  ⚠️  （読み込み不可）")
    
    # 最終統計を表示
    print("\n" + "=" * 50)
    print("処理結果")
    print("=" * 50)
    print(f"処理対象ファイル数: {len(files)}")
    print(f"機密情報が見つかったファイル数: {files_with_secrets}")
    print(f"検出された機密情報の総数: {total_secrets_found}")
    print(f"上書きされたファイル数: {files_overwritten}")
    print(f"作成されたバックアップファイル数: {backup_files_created}")
    
    if backup_files_created > 0:
        print(f"\n💡 元のファイルは .backup 拡張子で保存されています。")
        print(f"   問題がなければ、バックアップファイルは削除しても構いません。")
    
    print("\n✨ 処理が完了しました！")

if __name__ == "__main__":
    main()