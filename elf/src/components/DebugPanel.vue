<template>
    <div class="debugger">
        <h2>调试面板</h2>
        <form @submit.prevent="submitForm">
            <label>
                <span style="font-weight: bold;">用户名</span><br /> <!-- 添加换行 -->
                <input class="info-field" v-model="form.username" type="text"/>
            </label>
            <label>
                <span style="font-weight: bold;">我的坐标</span><br /> <!-- 添加换行 -->
                <input class="info-field" v-model="form.coordinate" type="text"/>
            </label>
            <label>
                <span style="font-weight: bold;">当前时间</span><br /> <!-- 添加换行 -->
                <input v-model="form.datetime" type="datetime-local" />
                <svg t="1710995521360" class="icon refresh-icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="2467" width="20" height="20" @click="refreshDatetime"><path d="M55.935033 264.48948c0 0 85.897017-132.548409 221.81443-203.673173 135.916406-71.121743 303.368504-50.646859 413.187968 18.319527 109.819465 68.970415 146.791894 127.160016 146.791894 127.160016l94.59499-53.879895c0 0 19.576483-9.697092 19.576483 12.932142l0 338.379961c0 0 0 30.17399-22.837719 19.395191-19.210878-9.062571-226.959086-127.198289-292.424528-164.466828-35.950145-16.035251-4.365101-29.062068-4.365101-29.062068l91.284402-52.173738c0 0-52.068992-65.209619-128.278989-99.744682-81.576231-42.501826-157.948384-47.541735-251.497925-12.224097-61.002644 23.025054-132.823368 81.988166-184.553949 169.082716L55.935033 264.48948 55.935033 264.48948 55.935033 264.48948zM904.056909 711.697844c0 0-85.897017 132.550423-221.816444 203.671159-135.917413 71.12275-303.366489 50.651895-413.186961-18.315498-109.825508-68.972429-146.790886-127.165052-146.790886-127.165052L27.662591 823.768348c0 0-19.572454 9.703135-19.572454-12.932142L8.090137 472.459267c0 0 0-30.170968 22.831676-19.397205 19.211885 9.067607 226.965129 127.198289 292.430571 164.470856 35.950145 16.035251 4.366109 29.058039 4.366109 29.058039l-91.285409 52.175753c0 0 52.071006 65.206598 128.279996 99.744682 81.57321 42.498804 157.942341 47.540728 251.496918 12.222082 60.998616-23.026061 132.820346-81.983131 184.546898-169.082716L904.056909 711.697844 904.056909 711.697844 904.056909 711.697844zM904.056909 711.697844" fill="#272636" p-id="2468"></path></svg>
                
            </label>
            <label>
                <span style="font-weight: bold;">短临描述</span><br /> <!-- 添加换行 -->
                <input class="info-field" v-model="form.nowcast" type="text" />
            </label>
            <label>
                <span style="font-weight: bold;">预报描述</span><br /> <!-- 添加换行 -->
                <input class="info-field" v-model="form.forecast" type="text" />
            </label>
            <label>
                <span style="font-weight: bold;">预警信息</span><br /> <!-- 添加换行 -->
                <input class="info-field" v-model="form.alert" type="text" />
            </label>
            <!-- 添加更多的表单字段... -->
            <button type="submit" style="margin-top: 10px;">触发</button>
            <textarea readonly v-model="logData" ref="logTextarea" style="width: 100%; height: 300px; font-size: 13px; margin-top: 10px; background-color: #FDF6E3; color: #7D8C8D;"></textarea>
        </form>
        <button @click="logData = ''" style="position: absolute; right: 10px; margin-top: 10px;">清屏</button>
    </div>
</template>

<script>
import { ref,onMounted, onUnmounted } from 'vue';
import axios from 'axios';

export default {
    setup() {
        function refreshDatetime() {
            const now = new Date();
            const year = now.getFullYear();
            const month = (now.getMonth() + 1).toString().padStart(2, '0');
            const date = now.getDate().toString().padStart(2, '0');
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            form.value.datetime = `${year}-${month}-${date}T${hours}:${minutes}`;
        }

        const now = new Date();
        const formatter = new Intl.DateTimeFormat('en', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false });
        const [{ value: month },,{ value: day },,{ value: year },,{ value: hour },,{ value: minute }] = formatter.formatToParts(now);
        const formattedDatetime = `${year}-${month}-${day}T${hour}:${minute}`;

        const form = ref({
            username: 'Clarmy',
            coordinate: '116.408293,39.918698', // 设置默认值
            datetime: formattedDatetime,
            nowcast: '',
            forecast: '',
            alert: '',
        });

        const submitForm = async () => {
            try {
                const response = await axios.post('http://0.0.0.0:8848/trigger', form.value);
                console.log(response.data);
            } catch (error) {
                console.error(error);
            }
            };

        const logData = ref('');
        const logTextarea = ref(null);
        let intervalId = null;

        onMounted(async () => {
            intervalId = setInterval(async () => {
                try {
                    const response = await axios.get('http://0.0.0.0:8848/log/?username=Clarmy');
                    if (!response.data.message) {
                        return;
                    }
                    logData.value += response.data.message + '\n';
                    logTextarea.value.scrollTop = logTextarea.value.scrollHeight;
                    console.log(logData.value);
                } catch (error) {
                    console.error(error);
                }
            }, 100);
        });

        onUnmounted(() => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        });

        return { form, logData, submitForm, refreshDatetime, logTextarea };
    },
};
</script>

<style scoped>
.debugger {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 500px; /* 调整为你需要的宽度 */
    padding: 20px;
    background-color: #f0f0f0; /* 调整为你需要的背景色 */
    overflow: auto;
}
label {
  display: block; /* 设置每个 <label> 标签为块级元素 */
  margin: 1px 0; /* 在上下方向添加 10px 的边距 */
  text-align: left;
}
.refresh-icon {
  margin-left: 10px;
  vertical-align: middle;
  cursor: pointer;
}
.info-field {
  width: 80%;
  padding: 5px;
  margin-top: 5px;
  font-size: 16px;
}
</style>