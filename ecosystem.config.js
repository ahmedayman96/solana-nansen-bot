module.exports = {
    apps: [
        {
            name: "solana-bot",
            script: "./main.py",
            interpreter: "/home/ubuntu/solana-nansen-bot/venv/bin/python",
            cwd: "./",
            watch: true,
            ignore_watch: ["*.db", "*.db-journal", "data/store.py"], // Ignore DB changes to prevent restart loops
            env: {
                PYTHONUNBUFFERED: "1",
                ...process.env
            }
        },
        {
            name: "solana-dashboard",
            script: "npm",
            args: "start", // Assumes 'npm run build' runs before
            cwd: "./dashboard",
            env: {
                PORT: 3000,
                HOSTNAME: "0.0.0.0", // Force binding to all IPv4 interfaces
                NODE_ENV: "production"
            }
        }
    ]
};
