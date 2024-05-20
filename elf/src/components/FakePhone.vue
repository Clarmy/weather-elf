<template>
    <div class="phone">
        <van-nav-bar
        title="智能提醒设置"
        left-text="返回"
        left-arrow
        @click-left="onClickLeft"
        />
        <!-- 在这里添加你的表单代码 -->
        <van-cell-group class="cellgroup" inset>
            <van-field label="用户名" v-model="username"  readonly/>
            <van-field
                v-model="cityName"
                is-link
                readonly
                label="关注城市"
                placeholder="选择城市"
                @click="showPicker = true"
                />
                <van-popup v-model:show="showPicker" round position="bottom">
                <van-picker
                    :columns="columns"
                    @cancel="showPicker = false"
                    @confirm="onConfirm"
                />
            </van-popup>
            <van-field
                v-model="concern"
                rows="2"
                autosize
                label="日常关注"
                type="textarea"
                maxlength="50"
                placeholder="我是一个码农，每天打车上下班，平时比较关心上下班时好不好打车"
                show-word-limit
            />
            <van-field
                v-model="scheduler"
                rows="2"
                autosize
                label="重要日程"
                type="textarea"
                maxlength="50"
                placeholder="这周六准备和老张去爬山"
                show-word-limit
            />
            <van-field name="rate" label="敏感度">
            <template #input>
                <van-rate v-model="rate" />
            </template>
            </van-field>
            
        </van-cell-group>
        <van-button class="spaced-button" type="primary" @click="submitForm">提交</van-button>

        <transition name="slide-fade">
        <div v-if="showNotification" class="notification">
            {{ notificationText }}
        </div>
        </transition>
    </div>
</template>

<script>
import { NavBar, showDialog } from 'vant';
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios'; // 导入 axios

export default {
    components: {
        [NavBar.name]: NavBar,
    },
    // 其他代码...
    setup() {
        const columns = [
        { text: '自动定位', value: 'Auto' },
        { text: '北京', value: 'Beijing' },
        { text: '上海', value: 'Shanghai' },
        { text: '广州', value: 'Guangzhou' },
        { text: '深圳', value: 'Shenzhen' },
        { text: '成都', value: 'Chengdu' },
        ];
    const cityName = ref('');
    const showPicker = ref(false);

    const onConfirm = ({ selectedOptions }) => {
      showPicker.value = false;
      cityName.value = selectedOptions[0].text;
    };

    const username= ref('Clarmy');   
    const concern = ref('');
    const scheduler = ref('');
    const rate = ref(0);

    onMounted(async () => {
      try {
        const response = await axios.get('http://0.0.0.0:8848/info?username=Clarmy');
        concern.value = response.data.concern; // 假设接口返回的数据中有 concern 字段
        scheduler.value = response.data.scheduler; // 假设接口返回的数据中有 scheduler 字段
        rate.value = response.data.rate; // 假设接口返回的数据中有 rate 字段
        cityName.value = response.data.cityname; // 假设接口返回的数据中有 cityname 字段
      } catch (error) {
        console.error(error);
      }
    });

    const submitForm = async () => {
      const payload = {
        username: username.value,
        cityname: cityName.value,
        concern: concern.value,
        scheduler: scheduler.value,
        rate: rate.value
      };

      console.log(payload);

      try {
        const response = await axios.post('http://0.0.0.0:8848/submit_info/', payload);
        console.log(response.data);
        showDialog({ message: '提交成功！', type: 'success' });
      } catch (error) {
        console.error(error);
        showDialog({ message: '提交失败！', type: 'fail' });
      }
    };

    const showNotification = ref(false);
    const notificationText = ref('');

    const showNotificationMessage = (message) => {
      notificationText.value = message;
      showNotification.value = true;

      setTimeout(() => {
        showNotification.value = false;
      }, 8000); // 3 秒后自动隐藏通知
    };

    onMounted(() => {
        const intervalId = setInterval(async () => {
            try {
            const response = await axios.get('http://0.0.0.0:8848/notification/?username=Clarmy');

            if (response.data.message) {
                showNotificationMessage(response.data.message);
            }
            } catch (error) {
            console.error('Failed to fetch notifications:', error);
            }
        }, 1000);

        onUnmounted(() => {
            clearInterval(intervalId);
        });
        });

    onUnmounted(() => {
      console.log('Component has been unmounted.');
    });

    return { username,  columns,
      onConfirm,
      cityName,
      showPicker, concern, scheduler, rate,submitForm,showNotification, notificationText, showNotificationMessage };
  },
};
</script>

<style scoped>
.phone {
    position: relative;
    width: 375px; /* iPhone 6/7/8 的宽度 */
    height: 667px; /* iPhone 6/7/8 的高度 */
    border: 2px solid #ccc;
    border-radius: 20px;
    overflow: hidden; /* 隐藏超出边界的内容 */
    background-color: #F7F8FA; /* 增加灰色背景色 */
}

.spaced-button {
  margin-top: 20px; /* 设置上边距为 20px */
}

.cellgroup {
  margin-top: 10px; /* 设置上边距为 10px */
}

.phone .van-popup {
  position: absolute;
  top: auto;
  bottom: 0;
  left: 0;
  right: 0;
  max-height: 50%;
  overflow: auto;
}

.notification {
    position: absolute;
    top: 10px;
    left: 50%;
    transform: translateX(-50%);
    padding: 10px;
    background-color: 	#808080;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    text-align: center;
    z-index: 9999; 
    transition: opacity .5s, transform .5s;
    width: 90%; /* 设置弹框的宽度为父元素宽度的90% */
    border-radius: 15px;
    color: white; 
}


.slide-fade-enter-active,
.slide-fade-leave-active {
    transition: opacity .5s; /* 只使用opacity过渡，移除transform */
}

.slide-fade-enter-from,
.slide-fade-leave-to {
    opacity: 0;
    /* 移除transform: translateY(-30px); 避免改变位置 */
}

</style>