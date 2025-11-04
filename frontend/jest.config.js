module.exports = {
preset: '@vue/cli-plugin-unit-jest/preset',
transform: {
'^.+\.vue$': '@vue/vue3-jest'
},
testEnvironment: 'jsdom',
collectCoverageFrom: ['src/**/*.{js,vue}', '!src/main.js']
}