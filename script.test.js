const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

const html = `<!DOCTYPE html><html><body><input id="display" value="0"></body></html>`;
const dom = new JSDOM(html);
global.document = dom.window.document;
global.window = dom.window;

eval(fs.readFileSync(path.resolve(__dirname, 'script.js'), 'utf-8'));

describe('Calculator Functions', () => {
    beforeEach(() => {
        clearDisplay();
    });

    test('Appends numbers correctly', () => {
        appendNumber('5');
        expect(document.getElementById('display').value).toBe('5');
    });

    test('Handles multiple number inputs', () => {
        appendNumber('3');
        appendNumber('2');
        expect(document.getElementById('display').value).toBe('32');
    });

    test('Appends decimal correctly', () => {
        appendNumber('7');
        appendDecimal();
        appendNumber('5');
        expect(document.getElementById('display').value).toBe('7.5');
    });

    test('Prevents multiple decimals', () => {
        appendNumber('4');
        appendDecimal();
        appendDecimal();
        appendNumber('2');
        expect(document.getElementById('display').value).toBe('4.2');
    });

    test('Handles addition correctly', () => {
        appendNumber('8');
        appendOperator('+');
        appendNumber('2');
        calculate();
        expect(document.getElementById('display').value).toBe('10');
    });

    test('Handles subtraction correctly', () => {
        appendNumber('9');
        appendOperator('-');
        appendNumber('3');
        calculate();
        expect(document.getElementById('display').value).toBe('6');
    });

    test('Handles multiplication correctly', () => {
        appendNumber('4');
        appendOperator('*');
        appendNumber('3');
        calculate();
        expect(document.getElementById('display').value).toBe('12');
    });

    test('Handles division correctly', () => {
        appendNumber('9');
        appendOperator('/');
        appendNumber('3');
        calculate();
        expect(document.getElementById('display').value).toBe('3');
    });

    test('Handles division by zero', () => {
        appendNumber('5');
        appendOperator('/');
        appendNumber('0');
        calculate();
        expect(document.getElementById('display').value).toBe('Error');
    });

    test('Clears display correctly', () => {
        appendNumber('8');
        clearDisplay();
        expect(document.getElementById('display').value).toBe('0');
    });

    test('Deletes last digit correctly', () => {
        appendNumber('45');
        deleteLast();
        expect(document.getElementById('display').value).toBe('4');
    });
});
