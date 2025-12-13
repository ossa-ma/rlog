/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
    preset: 'ts-jest',
    rootDir: '..',
    testEnvironment: 'node',
    transform: {
        '^.+\\.[tj]sx?$': ['ts-jest', {
            useESM: true,
        }],
    },
    transformIgnorePatterns: [
        'node_modules/(?!(node-fetch|data-uri-to-buffer|fetch-blob|formdata-polyfill)/)',
    ],
};
