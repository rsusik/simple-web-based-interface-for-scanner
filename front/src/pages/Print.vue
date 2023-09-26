<template>

  <q-page class="col text-center q-pt-md">
    <div v-if="inProgress" style="position: absolute; left:40%;">
      <q-circular-progress
        indeterminate
        size="100pt"
        :thickness="0.6"
        color="lime"
        center-color="grey-8"
        class="q-ma-md"
      />
    </div>
    <div v-if="filename != undefined" :style="{opacity: inProgress ? 0.5 : 1.0}">
      <q-img 
        v-if="filename.endsWith('.jpg') || filename.endsWith('.jpeg') || filename.endsWith('.png')"
        class="text-center"
        fit="contain"
        style="width: 128px; max-height: 128px; height: 128px; border: 1px solid #eee;"
        :img-style="{
          'min-width': '100%', 
          'min-height': '100%', 
          'object-fit': 'cover'
        }"
        :src="`${thumbnail_url}`"
        spinner-color="black" 
      />
      <q-icon 
        v-else-if="filename.endsWith('.pdf')"
        name="picture_as_pdf"
        class="text-center"
        fit="contain"
        size="64px"
        color="red"
      />
      <div><strong><a :href="image_url" style="font-size: 0.9rem;">{{filename}}</a></strong></div>
      <q-form @submit.prevent="startPrinting" class="q-mx-lg q-mt-lg">
        <q-select 
          v-model="quality" 
          :options="qualityOptions" 
          label="Quality" 
          outlined 
          class="q-mx-md q-my-xs" 
        />
        <q-select 
          v-model="sides" 
          :options="sidesOptions" 
          label="Sides" 
          outlined 
          class="q-mx-md q-my-xs" 
        />
        <q-select 
          v-model="orientation" 
          :options="orientationOptions" 
          label="Orientation" 
          outlined 
          class="q-mx-md q-my-xs" 
        />
        <q-input 
          v-model="pages" 
          label="Pages (empty for all)" 
          outlined 
          class="q-mx-md q-my-xs"
        />
        <q-btn 
          color="green" 
          :class="{'q-mt-md': $q.screen.gt.xs}"
          style="font-size: 1.5rem;" 
          type="submit"
          icon="scanner"
        >Print now</q-btn>
      </q-form>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from "vue";

export default defineComponent({
  name: "PageScan",

  data: function() {
    return {
      config: undefined,

      quality: 'default',
      qualityOptions: ['default', 'draft', 'normal', 'best'],
      sides: 'default',
      sidesOptions: ['default', 'one-sided', 'two-sided-long-edge', 'two-sided-short-edge'],
      orientation: 'default',
      orientationOptions: ['default', 'portrait', 'landscape'],
      pages: '',

      inProgress: false,
    }
  },

  computed: {
    filename: function() {
      let urlParams = (new URLSearchParams(window.location.hash.split('?')[1]))
      return urlParams.get("filename") ?? undefined
    },
    thumbnail_url: function() {
      if (this.config == undefined) {
        return undefined
      } else {
        return `http://${this.config.api_url}:${this.config.api_port}${this.config.scans_url}/thumbs/${this.filename}.thumb.jpg`
      }
    },
    image_url: function() {
      if (this.config == undefined) {
        return undefined
      } else {
        return `http://${this.config.api_url}:${this.config.api_port}${this.config.scans_url}/${this.filename}`
      }
    },
    print_url: function() {
      return `http://${this.config.api_url}:${this.config.api_port}/print/execute`
    },
  },


  created() {

  },

  mounted() {
    this.getJSON('config', 'config.json').then((config) => {
      this.config = config
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
          this.$q.notify({
            color: 'negative',
            message: `Error loading ${filename}`,
            icon: 'report_problem'
          })
          console.error(err)
          reject(err)
        })
      })
    },

    startPrinting: function () {
      this.inProgress = true;
      this.$axios.post(this.print_url, {
        filename: `${this.filename}`,
        quality: `${this.quality}`,
        orientation: `${this.orientation}`,
        sides: `${this.sides}`,
        pages: `${this.pages}`,
      }).then( (response) => {
        console.log(response)
        if (response.data.code == 0) {
          // success
          this.filename = response.data.filename
          this.$q.notify({
            color: 'positive',
            message: 'Job sent to printer'
          })
        } else {
          // error
          this.$q.notify({
            color: 'negative',
            message: 'Error while printing',
            icon: 'report_problem'
          })
          console.error(response)
        }
        this.inProgress = false
      }).catch( (err) => {
        // error
        this.$q.notify({
          color: 'negative',
          message: 'Error while printing',
          icon: 'report_problem'
        })
        console.error(err)
        this.inProgress = false
      })
    },


    getTypeFromFilename: function(filename) {
      let ext = filename.split('.').pop().toLowerCase()
      if (ext == 'png') {
        return 'png'
      } else if (['jpg', 'jpeg'].includes(ext)) {
        return 'jpeg'
      } else {
        throw 'Unsupported filetype.'
      }
    },


    // helper function: generate a new file from base64 String
    // from: https://gist.github.com/ibreathebsb/a104a9297d5df4c8ae944a4ed149bcf1
    dataURLtoFile: function (dataurl, filename) {
      const arr = dataurl.split(',')
      const mime = arr[0].match(/:(.*?);/)[1]
      const bstr = atob(arr[1])
      let n = bstr.length
      const u8arr = new Uint8Array(n)
      while (n) {
        u8arr[n - 1] = bstr.charCodeAt(n - 1)
        n -= 1 // to make eslint happy
      }
      return new File([u8arr], filename, { type: mime })
    },

    reloadImage: function (data) {
      //this.cropper.replace(this.image_url)
    },

    downloadImage: function () {
      var element = document.createElement('a');
      element.setAttribute('href', this.getImageData());
      element.setAttribute('download', this.filename);

      element.style.display = 'none';
      document.body.appendChild(element);

      element.click();

      document.body.removeChild(element);
    },

  }
});
</script>
