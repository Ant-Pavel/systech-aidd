/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    // Отключить линтер и проверку типов при сборке в Docker
    // (проверки делаются в CI отдельно или локально)
    eslint: {
        ignoreDuringBuilds: true,
    },
    typescript: {
        ignoreBuildErrors: true,
    },
}

module.exports = nextConfig

