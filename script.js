let display = document.getElementById('display');
let currentInput = '';
let operator = null;
let firstOperand = null;

function appendNumber(number) {
    if (currentInput === '0' && number !== '.') {
        currentInput = number;
    } else {
        currentInput += number;
    }
    updateDisplay();
}

function appendOperator(op) {
    if (currentInput === '' && firstOperand === null) return;

    if (firstOperand !== null) {
        calculate();
    }

    firstOperand = parseFloat(currentInput);
    operator = op;
    currentInput = '';
    updateDisplay();
}

function appendDecimal() {
    if (!currentInput.includes('.')) {
        currentInput += '.';
        updateDisplay();
    }
}

function calculate() {
    if (operator === null || firstOperand === null || currentInput === '') return;

    const secondOperand = parseFloat(currentInput);
    let result;

    switch (operator) {
        case '+':
            result = firstOperand + secondOperand;
            break;
        case '-':
            result = firstOperand - secondOperand;
            break;
        case '*':
            result = firstOperand * secondOperand;
            break;
        case '/':
            if (secondOperand === 0) {
                result = 'Error';
            } else {
                result = firstOperand / secondOperand;
            }
            break;
        default:
            return;
    }

    currentInput = String(result);
    operator = null;
    firstOperand = null;
    updateDisplay();
}

function clearDisplay() {
    currentInput = '';
    operator = null;
    firstOperand = null;
    updateDisplay();
}

function deleteLast() {
    currentInput = currentInput.slice(0, -1);
    updateDisplay();
    if (currentInput === '') {
        currentInput = '0';
        updateDisplay();
    }
}

function updateDisplay() {
    display.value = currentInput === '' ? '0' : currentInput;
}

// Initialize display
updateDisplay();