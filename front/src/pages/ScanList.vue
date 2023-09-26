<template>

  <q-page class="col">
      
      <q-list class="shadow-2 rounded-borders q-mx-lg q-my-lg" style="width: 96%;">
        <div v-if="this.pdflist.length > 0" class="row rounded-borders	 ">
          <q-input outlined v-model="pdffilename" label="Filename (optional)" class="q-ma-sm" />
          <q-btn label="Create PDF" icon="picture_as_pdf" @click="createPdf" class="q-ma-sm" color="red" />
        </div>
        <q-item v-for="item in items" :key="item" style="border-bottom: 1px solid #eee" >
          <q-item-section thumbnail>
            <q-btn v-if="!item.onpdflist && (item.filename.endsWith('png') || item.filename.endsWith('jpg'))" @click="addToPdfList(item.filename)" icon="picture_as_pdf" size="xs" outline rounded style="width: 10px; margin-left: 5px;" />
            <q-btn v-else-if="item.onpdflist" @click="removeFromPdfList(item.filename)" :label="getPdfListIndex(item.filename)" size="xs" outline rounded style="width: 10px; margin-left: 5px;" />
            <q-btn v-else size="xs" flat rounded style="width: 10px; margin-left: 5px;" disabled />
          </q-item-section>
          <q-item-section thumbnail>
            <div v-if="item.filename.endsWith('pdf')" 
              style="width: 128px; height: 128px; border: 1px solid #eee; vertical-align: middle; justify-items: center; align-items: center; display: flex; flex-direction: column; justify-content: center; align-content: center;" >
              <q-icon
                name="picture_as_pdf" 
                class="text-center"
                fit="contain"
                style="width: 128px; max-height: 128px; "
                size="64px"
                color="red"
              />
            </div>
            <q-img 
              v-else
              class="text-center"
              fit="contain"
              style="width: 128px; max-height: 128px; height: 128px; border: 1px solid #eee;"
              :img-style="{
                'min-width': '100%', 
                'min-height': '100%', 
                'object-fit': 'cover'
              }"
              :src="`${item.thumbnail}`"
              spinner-color="black" 
            />
          </q-item-section>
          <q-item-section style="overflow-wrap:break-word; hyphens: auto; word-break: break-all;">
            <a :href="item.src" style="font-size: 0.9rem;">{{item.filename}}</a>
            
          </q-item-section>
          <q-item-section avatar>
            <div class="row">
            <q-btn
              class="q-mr-sm"
              color="blue"
              label=""
              icon="print"
              size="sm"
              @click="printImage(item.filename)"
            />
            <q-btn
              color="red"
              label=""
              icon="delete"
              size="sm"
              @click="removeImage(item.filename)"
            />
            </div>
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
      config: undefined,
      pdflist: [],
      pdffilename: ''
    }
  },

  created: function () {

  },

  computed: {
    items: function() {
      return this.files.map( (file) => {
        return {
          filename: file.filename,
          src      : `http://${this.config.api_url}:${this.config.api_port}${this.config.scans_url}/${file.filename}`,
          thumbnail: `http://${this.config.api_url}:${this.config.api_port}${this.config.scans_url}/${file.thumbnail}`,
          type: this.getFileType(file.filename),
          onpdflist: this.pdflist.includes(file.filename)
        }
      })
    }
  },

  mounted() {
    this.getScanList()
  },

  methods: {

    getScanList: function() {
      this.getJSON('config', 'config.json').then((config) => {
        this.config = config
        this.$axios.get(`http://${this.config.api_url}:${this.config.api_port}/scans`)
        .then((response) => {
          if (response?.status == 200) {
            this.files = response.data.filenames
          } else {
            // error
            this.$q.notify({
              color: 'negative',
              message: 'Error loading scans',
              icon: 'report_problem'
            })
            console.error(response)
          }
        })
        .catch((err) => {
          // error
          this.$q.notify({
            color: 'negative',
            message: 'Error loading scans',
            icon: 'report_problem'
          })
          console.error(err)
        });
      })
    },
    
    addToPdfList: function(filename) {
      this.pdflist.push(filename)
    },

    removeFromPdfList: function(filename) {
      this.pdflist = this.pdflist.filter( (item) => {
        return item != filename
      })
    },

    getPdfListIndex: function(filename) {
      return this.pdflist.indexOf(filename) + 1
    },

    createPdf: function() {
      return new Promise((resolve, reject) => {
        this.$axios.post(`http://${this.config.api_url}:${this.config.api_port}/makepdf`, {
          target: this.pdffilename,
          filenames: this.pdflist
        })
        .then((response) => {
          if (response?.status == 200) {
            this.$q.notify({
              color: 'positive',
              message: 'PDF created',
              icon: 'done'
            })
            this.pdflist = []
            this.pdffilename = ''
            this.getScanList()
            // go to URL with scan: `http://${this.config.api_url}:${this.config.api_port}/files/${response.data.filename}`
            window.open(`http://${this.config.api_url}:${this.config.api_port}/files/${response.data.filename}`, '_blank')
          } else {
            // error
            this.$q.notify({
              color: 'negative',
              message: 'Error creating PDF. Make sure you have "convert" tool installed on server.',
              icon: 'report_problem'
            })
            console.error(response)
          }
        })
      })
    },

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
    getFileType: function(filename) {
      let ext = filename.split('.').pop().toLowerCase()
      if (['jpg', 'jpeg', 'png'].includes(ext)) {
        return 'img'
      } else {
        return 'other'
      }
    },
    removeImage: function(filename) {
      this.$axios.delete(`http://${this.config.api_url}:${this.config.api_port}/scans/${filename}`)
      .then((response) => {
        if (response?.status == 200) {
          this.files = this.files.filter( (item) => {
            return item.filename != filename
          })
        } else {
          // error
          this.$q.notify({
            color: 'negative',
            message: 'Error deleting image',
            icon: 'report_problem'
          })
          console.error(response)
        }
      })
      .catch((err) => {
        // error
        this.$q.notify({
          color: 'negative',
          message: 'Error deleting image',
          icon: 'report_problem'
        })
        console.error(err)
      });
    },
    printImage: function(filename) {
      this.$router.push({ path: '/print', query: { filename: filename } })
    }
  }


});
</script>
