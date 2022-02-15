<template>

  <q-page class="col text-center">
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
    <div v-if="filename == undefined" :style="{opacity: inProgress ? 0.5 : 1.0}">
      <h4>Set the parameters and start scanning</h4>
      <q-form @submit.prevent="startScan" class="q-mx-lg q-mt-lg">
        <q-select 
          v-model="format" 
          :options="formatOptions" 
          label="Output type" 
          outlined 
          class="q-mx-md q-my-xs" 
        />
        <q-select 
          v-model="resolution" 
          :options="resolutionOptions" 
          label="Resolution (dpi)" 
          outlined 
          class="q-mx-md q-my-xs" 
        />
        <q-select 
          v-model="mode" 
          :options="modeOptions" 
          label="Mode" 
          outlined 
          class="q-mx-md q-my-xs" 
        />
        <q-btn 
          color="green" 
          :class="{'q-mt-md': $q.screen.gt.xs}"
          style="font-size: 1.5rem;" 
          type="submit"
          icon="scanner"
        >Start scanning</q-btn>
      </q-form>
    </div>
    <div v-if="filename != undefined">
      <div class="row justify-center q-mt-lg">
        <div style="position:relative;">
          <img ref="img" :src="image_url" style="max-height:500px;" crossorigin="anonymous" />
        </div>
      </div>
      <div class="row justify-center">
        <div class="q-mr-md q-mb-md">
          <div>
            <a 
              :href="image_url" 
              class="q-my-md" 
              style="border: 1pt solid black; border-radius: 20pt; font-size: 22pt; padding: 8pt; text-decoration: none;"
              download
            >
              <q-icon name="download" />
              Download
            </a>
          </div>
          <div>Filename: {{filename}}</div>
        </div>

        <div class="text-center q-ml-md  q-mb-md">
          <div style="font-size: 1.5rem;">Set aspect ratio</div>
          <div>
            <q-btn 
              v-for="aspectRatio in aspectRatios" 
              :key="aspectRatio.label" 
              :label="aspectRatio.label" 
              @click="changeAspectRatio(aspectRatio.x, aspectRatio.y)"
              class="q-mx-xs"
            />
          </div>
          <q-btn v-if="cropper" class="q-my-lg" label="crop & save" @click="crop" />
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from "vue";
import Cropper from "cropperjs"
import 'cropperjs/dist/cropper.css';

export default defineComponent({
  name: "PageScan",

  data: function() {
    return {
      config: undefined,
      cropper: undefined,
      filename: undefined,
      aspectRatios: [
        {label: '1:1', x: 1, y: 1},
        {label: '2:3', x: 2, y: 3},
        {label: '4:3', x: 4, y: 3},
        {label: '16:9', x: 16, y: 9},
        {label: 'A4', x: 210, y: 297},
      ],
      format: 'png',
      formatOptions: ['png', 'jpg'],
      resolution: '150',
      resolutionOptions: ['75', '100', '150', '200', '250', '300', '600'],
      mode: 'color',
      modeOptions: ['color', 'gray'],
      inProgress: false
    }
  },

  computed: {
    image_url: function() {
      return `http://${this.config.api_url}:${this.config.api_port}${this.config.scans_url}/${this.filename}`
    },
    scan_url: function() {
      return `http://${this.config.api_url}:${this.config.api_port}/scan/execute`
    },
    image_update_url: function() {
      return `http://${this.config.api_url}:${this.config.api_port}/scan/update`
    }
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
          console.log(err)
          reject(err)
        })
      })
    },

    startScan: function () {
      this.inProgress = true;
      this.$axios.post(this.scan_url, {
        //params: {
          format: `${this.format}`,
          resolution: `${this.resolution}`,
          mode: `${this.mode}`,
        //}
      }).then( (response) => {
        console.log(response)
        if (response.data.code == 0) {
          // success
          this.filename = response.data.filename
        } else {
          // error
        }
        this.inProgress = false
      }).catch( (err) => {
        // error
        this.inProgress = false
      })
    },

    createCropper: function () {
      this.cropper = new Cropper(this.$refs.img, {
        viewMode: 2,
        crop(event) {
          // console.log(event.detail.x);
          // console.log(event.detail.y);
          // console.log(event.detail.width);
          // console.log(event.detail.height);
          // console.log(event.detail.rotate);
          // console.log(event.detail.scaleX);
          // console.log(event.detail.scaleY);
        },
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

    changeAspectRatio: function (x, y) {
      if (this.cropper == undefined) {
        this.createCropper()
      }
      this.cropper.setAspectRatio(x / y)
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

    getImageData: function () {
      if (this.cropper == undefined) {
        // TODO: need to be fixed
        const cvs = document.createElement('canvas')
        cvs.width = this.$refs.img.width
        cvs.height = this.$refs.img.height
        cvs.getContext('2d').drawImage(this.$refs.img, 0, 0)

        return cvs.toDataURL()
      } else {
        return this.cropper.getCroppedCanvas().toDataURL(`image/${this.getTypeFromFilename(this.filename)}`)
      }
    },

    crop: function () {
      let cropped = this.cropper.getCroppedCanvas().toDataURL(`image/${this.getTypeFromFilename(this.filename)}`)
      const file = this.dataURLtoFile(cropped, this.filename)
      var formData = new FormData();
      formData.append("file", file, file.name)
      this.$axios.post(this.image_update_url, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
      })
      .then((res) => {
        //...
        console.log('done')
        console.log(res)
        this.reloadImage()
      })
      .catch((err) => {
        //...
        console.log('problem')
        console.log(err)
      })

    }

  }


});
</script>
