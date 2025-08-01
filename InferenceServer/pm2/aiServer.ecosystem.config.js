module.exports = {
  apps: [
    /* aiServer */
    {
      name: "aiServer",
      cwd: "./",
      script: "./aiServer/main.py",
      autorestart: false,
      watch: true,
      env: {
        PYTHON_ENV: "development",
        PROCESS_NAME: "aiServer",
        APP_INSTANCE_ID : "0",
      },
      env_production: {
        PYTHON_ENV: "production",
        PROCESS_NAME: "aiServer",
        APP_INSTANCE_ID : "0",
      },
      // 가상 환경 python 경로.
      // interpreter: '~\Anaconda3\envs\newTensor\python'
    },
  ],
};
