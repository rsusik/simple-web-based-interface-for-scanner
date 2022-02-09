<template>

  <q-page class="flex flex-center">
      <q-list class="shadow-2 rounded-borders q-mx-lg q-my-lg" style="width: 100%;">
        <q-item v-for="item in items" :key="item" style="border-bottom: 1px solid #eee" >
          <q-item-section thumbnail>
            <q-img 
              class="rounded-borders"
              fit="contain"
              style="width: 128px; max-height: 128px; border: 1px solid #eee"
              :ratio="1" 
              :src="`${item.src}`"
              spinner-color="black" 
            />
          </q-item-section>
          <q-item-section style="overflow-wrap:break-word; hyphens: auto; word-break: break-all;">
            <a :href="item.src">{{item.filename}}</a>
            
          </q-item-section>
        </q-item>
      </q-list>
  </q-page>
</template>

<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "PageScanList",

  data: function() {
    return {
      files: [],
      config: undefined
    }
  },

  created: function () {

  },

  computed: {
    items: function() {
      return this.files.map( (filename) => {
        return {
          filename: filename,
          src: `http://${this.config.api_url}:${this.config.api_port}${this.config.scans_url}/${filename}`,
          type: this.getFileType(filename)
        }
      })
    }
  },

  mounted() {
    this.getJSON('config', 'config.json').then((config) => {
      this.config = config
      this.$axios.get(`http://${this.config.api_url}:${this.config.api_port}/scans`)
      .then((response) => {
        if (response?.status == 200) {
          this.files = response.data
        } else {
          // error
        }
      })
      .catch(function (err) {
        // error
      });
    })
  },

  methods: {
    getJSON: function (target, filename) {
      return new Promise((resolve, reject) => {
        this.$axios.get(filename).
        then((resp) => {
          let jsonData = resp.data
          localStorage.setItem(target, JSON.stringify(jsonData))
          resolve(jsonData)
        })
        .catch((err) => {
          // error
          console.log(err)
          reject(err)
        })
      })
    },
    getFileType: function(filename) {
      let ext = filename.split('.').pop().toLowerCase()
      if (['jpg', 'jpeg', 'png'].includes(ext)) {
        return 'img'
      } else {
        return 'other'
      }
    },
  }


});
</script>
