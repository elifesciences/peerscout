export const groupBy = (a, kf) => a.reduce((o, item) => {
  o[kf(item)] = item;
  return o;
}, {});

export const groupByMultiple = (a, kf) => a.reduce((o, item) => {
  const groupedList = o[kf(item)];
  if (groupedList) {
    groupedList.push(item);
  } else {
    o[kf(item)] = [item];
  }
  return o;
}, {});

export const flatMap = (a, f) => [].concat(...a.map(f));

export const range = size => {
  const a = [];
  for (let i = 0; i < size; i++) {
    a.push(i);
  }
  return a;
}
