<template>

  <q-page class="col text-center">
    <div v-if="filename == undefined" :style="{opacity: inProgress ? 0.5 : 1.0}">
      
    <div class="full-width justify-center items-center q-my-sm">
      <q-uploader
        :url="upload_url"
        class="q-my-md"
        style="
          min-height: 200px;
          border: 3pt dashed silver;
          max-width: 1024px;
          width: 100%;
          margin: auto auto;
        "
        color="transparent"
        text-color="black"
        label="Upload files"
        field-name="file"
        accept=".jpg, image/*, .pdf"
        max-files="1"
        :multiple="false"
        auto-upload
        with-credentials
        @uploaded="uploaded"
        @uploading="uploading"
        @failed="uploadFailed"
        @factory-failed="factoryFailed"
        @rejected="rejected"
        @finish="uploadFinish"
        :headers="[{'Authorization': `Bearer ${token}`}]"
        :factory="uploadFactory"
        :disable="image != undefined"
      >
          <template v-slot:header="scope">
            <div 
              class="row no-wrap text-grey-4 text-uppercase items-center q-pa-sm q-gutter-xs justify-center items-center" 
              :class="{'hidden': scope.uploadedFiles.length>0}"
              style="
                position: absolute; 
                top: 0px; 
                z-index: 1; 
                font-size: 2.8rem;
                font-family: sans-serif;
                margin-left: auto;
                margin-right: auto;
                left: 0;
                right: 0;
                text-align: center;
              "
            >Drag & drop here</div>
            <div 
              class="row no-wrap q-pa-sm q-gutter-xs justify-center items-center" 
              :class="{'hidden': scope.uploadedFiles.length>0}"
              style="position: absolute; top:70px; margin-left: auto;
    margin-right: auto;
    left: 0;
    right: 0; z-index:5;"
            >
              <q-circular-progress
                v-if="fileUploading" 
                indeterminate
                size="50px"
                color="red"
                :thickness="1"
                track-color="grey-3"
                class="q-ma-md"
              />
              <q-btn 
                v-if="scope.canAddFiles" 
                type="a" 
                icon="add_box" 
                label="Upload file"
                outline
                class="bg-white"
              ><!--@click="scope.pickFiles"-->
                <q-uploader-add-trigger />
                <q-tooltip>Click to pick a file</q-tooltip>
              </q-btn>
            </div>
          </template>
      </q-uploader>
      <!-- ALTERNATYWNIE:
      <input type="file" @change="uploadFile($event)" >
      -->
    </div>
    </div>
    <div v-if="filename != undefined">
      <div class="row justify-center q-mt-lg q-mb-md">
        <div style="position:relative;">
          <img ref="img" :src="image_url" style="max-height:500px;" crossorigin="anonymous" />
        </div>
      </div>
      <div class="col justify-center">
        <div class="q-mr-md q-mb-md">
          <div style="margin-bottom: 5pt">
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
      fileUploading: false,
      filename: undefined,
      
      format: undefined, // 'png',
      formatOptions: ['png', 'jpg'],
      resolution: undefined, // '150',
      resolutionOptions: ['75', '100', '150', '200', '250', '300', '600'],
      mode: undefined, // 'color',
      modeOptions: ['color', 'gray'],
      inProgress: false,
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
    },
    upload_url: function() {
      return `http://${this?.config?.api_url}:${this?.config?.api_port}/upload` ?? ''
    },
  },

  watch: {
    resolution: function (val) {
      localStorage.setItem('resolution', val)
    },
    format: function (val) {
      localStorage.setItem('format', val)
    },
    mode: function (val) {
      localStorage.setItem('mode', val)
    },
  },

  created() {
    this.resolution = localStorage.getItem('resolution') ?? '150';
    this.format = localStorage.getItem('format') ?? 'png';
    this.mode = localStorage.getItem('mode') ?? 'color';
    this.randVal = Math.random()
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
          this.$q.notify({
            color: 'negative',
            message: 'Error starting scan',
            icon: 'report_problem'
          })
          console.error(response)
        }
        this.inProgress = false
      }).catch( (err) => {
        // error
        this.$q.notify({
          color: 'negative',
          message: 'Error starting scan',
          icon: 'report_problem'
        })
        console.error(err)
        this.inProgress = false
      })
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




    // uploadFactory: function(file) {
    //   return new Promise((resolve, reject) => {
    //       resolve()
    //   })
    // },

    uploadFailed: function(info) {
      this.$q.notify({
          color: 'negative',
          message: 'Unable to upload the file. Let us know if the problem repeats.',
          // icon: 'check'
        })
    },

    rejected: function(info) {
      this.$q.notify({
          color: 'negative',
          message: 'File rejected. Make sure that the file size do not exceed the limit.',
          // icon: 'check'
        })
    },

    // factoryFailed: function(err, files) {
    //   this.$q.notify({
    //       color: 'negative',
    //       message: 'Some error occured while uploading the file. It may be caused by connection issue. Please contact our support if the problem repeats.',
    //       // icon: 'check'
    //     })
    //   console.log(err)
    // },

    uploading: function(info) {
      this.fileUploading = true
    },

    uploaded: function(info) {
      this.$q.notify({
        color: 'positive',
        message: 'Image successfuly uploaded!',
        icon: 'check'
      })
      // console.log('info:')
      // console.log(info)
      // console.lodfdfg()
      // redirect to print
      let filename = JSON.parse(info.xhr.response).filename
      this.$router.push({ path: '/print', query: { filename: filename } })
      // this.image = {}
      // Object.assign(this.image, JSON.parse(info.xhr.response))
    },

    uploadFinish: function(info) {
      // this.fileUploading = false
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

    
  }
});
</script>
