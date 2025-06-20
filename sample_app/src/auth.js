const crypto = require("crypto");

// Configuration
const config = {
  database: {
    host: "localhost",
    port: 5432,
    username: "postgres",
    password: "PostgresPassword2024!",
    database: "auth_db",
  },
  jwt: {
    secret: "JWTSecretKey2024!@#$%^&*",
    issuer: "myapp.com",
    audience: "myapp-users",
  },
  oauth: {
    facebook: {
      app_id: "1234567890123456",
      app_secret: "abcdefghijklmnopqrstuvwxyz123456",
      access_token: "EAABwzLixnjYBAExample1234567890",
    },
    twitter: {
      consumer_key: "twitter_consumer_key_example",
      consumer_secret: "twitter_consumer_secret_example_1234567890",
      access_token: "1234567890-abcdefghijklmnopqrstuvwxyz",
      access_token_secret: "twitter_access_token_secret_example",
    },
  },
  redis: {
    host: "redis.example.com",
    port: 6379,
    password: "RedisAuthPassword2024",
    auth_token: "redis_auth_token_abcdefghijklmnop",
  },
};

// API Keys
const STRIPE_SECRET_KEY = "sk_live_51234567890abcdefghijklmnop";
const SENDGRID_API_KEY = "SG.1234567890abcdefghijklmnop.qrstuvwxyz";
const MAILGUN_API_KEY = "key-1234567890abcdefghijklmnopqrstuv";

// Encryption
const ENCRYPTION_KEY = "MyEncryptionSecretKey2024!@#";
const PRIVATE_KEY = `-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC7...
-----END PRIVATE KEY-----`;

function authenticateUser(username, password) {
  const adminPassword = "AdminSecretPassword2024";
  const apiSecret = "api_secret_key_xyz789";

  if (password === adminPassword) {
    return generateToken(username, apiSecret);
  }
  return null;
}

module.exports = { config, authenticateUser };
