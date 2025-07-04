<template>
  <div id="app" class="container">
    <h3>Download MP3 from YouTube</h3>
    <section v-if="errorDownload">
      <div class="alert alert-dismissible alert-danger">
        <strong>Something goes wrong.</strong>
        {{ errorDownloadMsg }}
        <a href="/">Convert again</a>.
      </div>
    </section>
    <div class="row" v-show="formUrl">
      <div class="col-xl-8">
        <div class="form-group">
          <input
            onfocus="this.value=''"
            v-model.trim="$v.urlToDownload.$model"
            class="form-control"
            :class="status($v.urlToDownload)"
            id="downloadTarget"
            aria-describedby="downloadHelp"
            placeholder="Input your favorite youtube URL"
          />
          <small
            id="downloadHelp"
            class="form-text text-muted d-none d-sm-block"
          >For example: https://www.youtube.com/watch?v=kJQP7kiw5Fk</small>
          <div
            v-if="!$v.urlToDownload.url"
            class="error invalid-feedback"
          >It does't look like an URL.</div>
          <div v-if="!$v.urlToDownload.required" class="error invalid-feedback">URL is required.</div>
        </div>
      </div>
      <div clas="col-xl-2">
        <div class="form-group mr-2 ml-3"> 
          <select id="audioQuality" class="form-control custom-select" v-model="audioQuality">
            <option value="128">128 kbps</option>
            <option value="192">192 kbps</option>
            <option value="256">256 kbps</option>
            <option value="320">320 kbps</option>
          </select>
          <small id="audioQualityHelp" class="form-text text-muted d-none d-sm-block">Audio quality</small>
        </div>
      </div>
      <div clas="col-xl-2">
        <div class="form-group mr-2 ml-3">
          <select id="audioFormat" class="form-control custom-select" v-model="audioFormat">
            <option value="mp3">MP3</option>
            <option value="aac">AAC</option>
          </select>
           <small id="audioFormatHelp" class="form-text text-muted d-none d-sm-block">Audio format</small>
        </div>        
      </div>
      <div clas="col-xl-2">
        <div class="form-group">
          <button
            :disabled="isDisabled"
            v-on:click.once="downloadLink"
            class="btn btn-primary form-control"
          >Submit</button>
        </div>
      </div>
    </div>
    <div class="row" style="margin-top:5px;margin-bottom:10px" v-show="progressBar">
      <div class="col-xl-4" v-show="progressInfo">
        <span class="form-text" id="progress-info">Starting ...</span>
      </div>
    </div>
    <section v-if="downloadSuccess">
      <div class="alert alert-dismissible alert-success">
        <a :href="urlForDownload" target="blank">Download Here</a>. The link is available for 10 minutes.
        <a href="/">Convert again</a>.
        <div id="DBButton"></div>
      </div>
    </section>
    <div v-if="popularVideoContainer" class="row">
      <div class="jumbotron">
        <h4 class="text-primary">Popular Videos</h4>
        <p class="lead d-none d-sm-block">In case you just get bored ...</p>
        <hr class="my-3" />
        <!--
        <iframe width="560" height="315" src="https://www.youtube.com/embed/FJnTGLZPBaE" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
          <iframe width="560" height="315" src="https://www.youtube.com/embed/Jcmolh5Yw-0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
          <iframe width="560" height="315" src="https://www.youtube.com/embed/crM2e00j10o" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
          <iframe width="560" height="315" src="https://www.youtube.com/embed/-N_REC0MNGg" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        -->
        <div class="card-columns">
          <video-card
            v-for="video in popular_videos"
            v-bind:key="video.id"
            v-bind:videoid="video.id"
            v-bind:thumbnail="video.thumb"
            v-bind:title="video.title"
          ></video-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import axios from "axios";
import Vuelidate from "vuelidate";
import { required, url } from "vuelidate/lib/validators";
import ClipboardJS from "clipboard";
import VideoCard from "./components/VideoCard.vue";

/* Load style */
import "./css/main.css";
import "./css/custom.css";

/* Fixed FB Login */
///IE & Chrome
if (String(window.location.hash).substring(0, 1) == "#") {
  window.location.hash = "";
  window.location.href = window.location.href.slice(0, -1);
}
// Firefox version of the hack
if (String(location.hash).substring(0, 1) == "#") {
  location.hash = "";
  location.href = location.href.substring(0, location.href.length - 3);
}
/* End of Fixed FB Login*/
/* Generate Client ID for websocket*/
const guid = () =>
  Math.random()
    .toString(36)
    .substring(2, 15) +
  Math.random()
    .toString(36)
    .substring(2, 15);

const converter_id = guid();
/* Adapt to Vue.js */
function getYoutubeVideo() {
  var youtube = document.querySelectorAll(".youtube");
  for (var i = 0; i < youtube.length; i++) {
    var source = youtube[i].dataset.img;
    var image = new Image();
    image.className = "card-img-top";
    image.src = source;
    image.addEventListener(
      "load",
      (function() {
        youtube[i].appendChild(image);
      })(i)
    );
    youtube[i].addEventListener("click", function() {
      var iframe = document.createElement("iframe");
      iframe.setAttribute("frameborder", "0");
      iframe.setAttribute("allowfullscreen", "");
      iframe.setAttribute(
        "src",
        "https://www.youtube.com/embed/" +
          this.dataset.embed +
          "?rel=0&showinfo=0&autoplay=1"
      );
      this.innerHTML = "";
      this.appendChild(iframe);
    });
  }
}

function createDBButton(url, filename) {
  var options = {
    files: [
      {
        url: url,
        filename: filename
      }
    ],
    success: function() {
      alert("Success! File saved to your Dropbox.");
    },
    cancel: function() {},
    error: function(errorMessage) {
      console.log(errorMessage);
    }
  };
  var button = Dropbox.createSaveButton(options);
  document.getElementById("DBButton").appendChild(button);
}

Vue.use(Vuelidate);
export default {
  name: "app",
  components: {
    VideoCard
  },
  data() {
    return {
      progressInfo: false,
      progressBar: false,
      enableDownloadButton: true,
      errorDownload: false,
      errorDownloadMsg: null,
      urlToDownload: null,
      textLoading: false,
      urlForDownload: null,
      downloadSuccess: false,
      formUrl: true,
      audioFormat: "mp3",
      audioQuality: "128",
      popularVideoContainer: false,
      popular_videos: null
    };
  },
  mounted: function() {
  if(window.location.pathname === '/'){
    axios
      .get("/popular?limit=15")
      .then(response => {
        this.popularVideoContainer = true;
        this.popular_videos = JSON.parse(response.data);
      })
      .catch(error => {
        //console.log(error);
        this.errorDownload = true;
      });
    }
  },
  validations: {
    urlToDownload: {
      required,
      url
    }
  },
  computed: {
    isDisabled: function() {
      return !this.enableDownloadButton;
    }
  },
  methods: {
    status(validation) {
      return {
        "is-invalid": validation.$error,
        "is-valid": validation.$dirty
      };
    },
    downloadLink() {
      this.enableDownloadButton = false;
      let filename = null;
      this.errorDownload = false;
      this.progressInfo = true;
      this.progressBar = true;
      $("#progress-info").html("Processing, please wait a few seconds...");

      // Process to download
      axios
        .post("/convert", {
          name: converter_id,
          urls: this.urlToDownload,
          audio_quality: this.audioQuality,
          audio_format: this.audioFormat
        })
        .then(res => {
          let result = JSON.parse(res.data);
          console.log(result);
          if (result.status == true) {
            filename = result.data.filename;
            var path = result.data.path;
            this.urlForDownload = "file/" + path + "." + this.audioFormat;
            this.downloadSuccess = true;
            this.formUrl = false;
            this.progressBar = false;
          } else {
            this.formUrl = false;
            this.errorDownload = true;
            this.progressBar = false;
            this.errorDownloadMsg = result.error;
          }
        })
        .catch(error => {
          this.progressBar = false;
          this.errorDownload = true;
        })
        .finally(() => {
          //this.spinner_loading = false;
          this.formUrl = false;
          if (this.errorDownload === false) {
            createDBButton(
              encodeURI(
                "https://" +
                  window.location.hostname +
                  "/" +
                  this.urlForDownload
              ),
              unescape(filename)
            );
          }
        });
    }
  },
  updated() {
    getYoutubeVideo();
    new ClipboardJS(".btn");
  }
};
</script>