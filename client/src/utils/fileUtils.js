export const readFileAsText = file => new Promise((resolve, reject) => {
  try {
    const reader = new FileReader();
    reader.onerror = event => {
      console.err("error:", event);
      reject(event);
    }
    reader.onload = () => {
      const text = reader.result;
      // console.log("onload:", text);
      resolve(text);
    };
    reader.readAsText(file);
  } catch (e) {
    reject(e);
  }
});
