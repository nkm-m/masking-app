# 🔒 Secret Masking Tool

A powerful Python tool that automatically detects and masks sensitive information in your codebase to prevent accidental exposure of secrets.

## 🌟 Features

- **Comprehensive Detection**: Automatically detects passwords, API keys, tokens, AWS credentials, and other sensitive data
- **Multi-format Support**: Works with various file types (.py, .js, .php, .yml, .json, .properties, .env, etc.)
- **Safe Processing**: Creates backups before overwriting files
- **Pattern Recognition**: Supports multiple secret patterns including:
  - Database passwords and connection strings
  - API keys (Stripe, AWS, Google, GitHub, etc.)
  - JWT tokens and session secrets
  - OAuth credentials
  - Encryption keys and certificates

## 🚀 Quick Start

### Prerequisites
- Python 3.6 or higher

### Installation
1. Clone this repository:
```bash
git clone https://github.com/your-username/secret-masking-tool.git
cd secret-masking-tool
```

2. No additional dependencies required - uses only Python standard library!

### Usage

1. **Place your files/directories** that contain sensitive information in the same directory as `mask_secrets.py`

2. **Run the masking tool**:
```bash
python mask_secrets.py
```

3. **Follow the prompts** - the tool will ask for confirmation before processing

4. **Review results** - sensitive data will be replaced with `***` and original files will be backed up with `.backup` extension

## 📁 Directory Structure
```
secret-masking-tool/
├── mask_secrets.py          # Main masking tool
├── sample_app/              # Sample application with test data
│   ├── config/
│   ├── src/
│   ├── docker/
│   └── .env
└── README.md
```

## 🧪 Try with Sample Data

This repository includes a sample application with various types of sensitive information for testing:

1. **Run the masking tool**:
```bash
python mask_secrets.py
```

2. **Check the results** in the `sample_app` directory to see how different types of secrets are masked

## 🔍 Supported Secret Types

| Type | Examples |
|------|----------|
| **Passwords** | `password: "secret123"`, `DB_PASS = "mypass"` |
| **API Keys** | `api_key: "sk_test_123..."`, `STRIPE_SECRET_KEY=sk_live_...` |
| **Tokens** | `auth_token: "abc123"`, `JWT_SECRET=mysecret` |
| **AWS Credentials** | `AKIA...` (Access Keys), `wJalr...` (Secret Keys) |
| **Database URLs** | `postgresql://user:pass@host/db` |
| **OAuth Secrets** | `client_secret: "oauth_secret"` |
| **Encryption Keys** | `encryption_key: "mykey123"` |

## ⚙️ How It Works

1. **Scans** all files in the current directory and subdirectories
2. **Detects** sensitive information using regex patterns
3. **Creates backups** of original files (`.backup` extension)
4. **Masks secrets** by replacing sensitive values with `***`
5. **Provides statistics** on processed files and found secrets

## 🛡️ Safety Features

- **Backup Creation**: Original files are automatically backed up
- **User Confirmation**: Asks for permission before making changes
- **Exclusion Patterns**: Skips already processed files and system files
- **Error Handling**: Graceful handling of encoding issues and file access errors

## 📊 Example Output

```
==================================================
機密情報マスキングツール（上書き版）
==================================================
作業ディレクトリ: /path/to/your/project

検出パターン数: 45
処理対象ファイル数: 8

📁 config/database.yml
  ⚠️  機密情報が 3 件見つかりました:
    1. 'password: "DevPassword123!"'
    2. 'password: "SuperSecretProd2024"'
    3. 'api_token: "prod-token-abc123def456"'
  🔒 マスキングを実行しています...
  💾 バックアップ作成: config/database.yml.backup
  ✅ ファイル上書き完了

==================================================
処理結果
==================================================
処理対象ファイル数: 8
機密情報が見つかったファイル数: 6
検出された機密情報の総数: 24
上書きされたファイル数: 6
作成されたバックアップファイル数: 6

✨ 処理が完了しました！
```

## ⚠️ Important Notes

- **Always backup your code** before running this tool on important projects
- **Review the results** to ensure no legitimate data was accidentally masked
- **Test thoroughly** after masking to ensure your application still works correctly
- **Keep backup files** until you're confident the masking was successful

---

**⚠️ Disclaimer**: This tool is designed to help prevent accidental exposure of secrets. Always review the results and maintain proper security practices in your development workflow.
