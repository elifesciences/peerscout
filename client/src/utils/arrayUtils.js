export const flatMap = (a, f) => [].concat(...a.map(f));

export const range = size => {
  const a = [];
  for (let i = 0; i < size; i++) {
    a.push(i);
  }
  return a;
}
