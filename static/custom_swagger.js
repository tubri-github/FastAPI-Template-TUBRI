document.addEventListener('DOMContentLoaded', function() {
  const apiKeyInput = document.querySelector('input[name=x-api-key]');

  // listen action of API input field
  apiKeyInput.addEventListener('change', async function() {
    const apiKeyValue = this.value;
    try {
      // send post to backend, get options
      const response = await fetch('/api/get-options', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKeyValue  // send API as header
        }
      });

      if (response.ok) {
        const options = await response.json();
        const multiSelect = document.querySelector('tr[data-param-name="dataset"] select[multiple]'); // 根据实际情况替换选择器

        // clear current options
        while (multiSelect.firstChild) {
          multiSelect.removeChild(multiSelect.firstChild);
        }

        // add new options
        options.forEach(option => {
          const optionElement = document.createElement('option');
          optionElement.value = option;
          optionElement.text = option;
          multiSelect.appendChild(optionElement);
        });
      } else {
        console.error('Failed to retrieve options');
      }
    } catch (error) {
      console.error('Error fetching options:', error);
    }
  });
});
