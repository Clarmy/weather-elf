import { createApp } from 'vue';
import App from './App.vue';
import { Picker, Field, CellGroup, Rate, Button, Popup, Dialog } from 'vant';
import 'vant/lib/index.css';

const app = createApp(App);
app.use(Picker);
app.use(Field);
app.use(CellGroup);
app.use(Rate);
app.use(Button);
app.use(Popup);
app.use(Dialog);

app.mount('#app');