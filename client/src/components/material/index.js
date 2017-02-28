export { default as AppBar } from 'material-ui/AppBar';
export { default as Checkbox } from 'material-ui/Checkbox';
export { default as Chip } from 'material-ui/Chip';
export { default as FlatButton } from 'material-ui/FlatButton';
export { default as Drawer } from 'material-ui/Drawer';
export { default as Divider } from 'material-ui/Divider';
export { default as MenuItem } from 'material-ui/MenuItem';
export { default as Paper } from 'material-ui/Paper';
export { default as RaisedButton } from 'material-ui/RaisedButton';
export { default as TextField } from 'material-ui/TextField';
export { default as Toggle } from 'material-ui/Toggle';
export { default as SelectField } from 'material-ui/SelectField';
export { default as Slider } from 'material-ui/Slider';
export { default as Snackbar } from 'material-ui/Snackbar';

import SelectField from 'material-ui/SelectField';
import MenuItem from 'material-ui/MenuItem';
SelectField.Item = MenuItem;

import { Tabs, Tab } from 'material-ui/Tabs';
Tabs.Tab = Tab;

export {
  Tabs, Tab
}

export * from 'material-ui/Card';

// export { default as Button } from './Button';

//export * from './floatingActionButtons';
