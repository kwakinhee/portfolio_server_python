module.exports = {
  apps: [
    /* configServer */
    {
      name: "configServer",
      cwd: "./",
      script: "./configServer/main.py",
      autorestart: false,
      watch: true,
      env: {
        NODE_ENV: "development",
        PROCESS_NAME: "configServer",
      },

      env_production: {
        NODE_ENV: "production",
        PROCESS_NAME: "configServer",
      },
    },
  ],
};
