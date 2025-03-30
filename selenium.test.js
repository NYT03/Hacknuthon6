const { Builder, By, until } = require('selenium-webdriver');

// Get the file path from command line arguments
const filePath = process.argv[2];

(async function testCalculator() {
    let driver = await new Builder().forBrowser('chrome').build();

    try {
        // Open your calculator webpage (adjust the path accordingly)
        await driver.get('D:/HackNuthon_6/Hacknuthon6/index.html');

        // Get display element
        let display = await driver.findElement(By.id('display'));

        // Click numbers and operators
        await driver.findElement(By.css("[onclick=\"appendNumber('5')\"]")).click();
        await driver.findElement(By.css("[onclick=\"appendOperator('+')\"]")).click();
        await driver.findElement(By.css("[onclick=\"appendNumber('3')\"]")).click();
        await driver.findElement(By.css("[onclick=\"calculate()\"]")).click();

        // Wait for the result to be displayed
        await driver.wait(until.elementLocated(By.id('display')), 5000); // Wait for the display element to be located
        let result;
        // Polling to check the display value
        for (let i = 0; i < 10; i++) {
            result = await display.getAttribute('value');
            if (result === '8') {
                console.log('Test Passed: 5 + 3 =', result);
                break;
            }
            await driver.sleep(500); // Wait before checking again
        }

        if (result !== '8') {
            console.error('Test Failed: Expected 8 but got', result);
        }
    } catch (err) {
        console.error('Test Failed:', err);
    } finally {
        await driver.quit(); // Close browser
    }
})();