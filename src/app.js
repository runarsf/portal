var app = new Vue({
  el: '#app',
  data: {
    categories: [],
    time: ''
  },
  methods: {
    fetchLinks: function (url) {
      fetch(url)
        .then(response => {
            if (!response.ok) throw Error(response.statusText)
            return response.json()})
        .then(response => this.categories = response)
        .catch(error => {
          console.error(error);
          console.log(`Error when trying to fetch ${url}, defaulting to sample-links.json`)
          this.fetchLinks('sample-links.json')
        })
    },
    updateTime: function () {
      var today = new Date()
      var h = today.getHours()
      var m = today.getMinutes()
      var s = today.getSeconds()
      if (m < 10) { m = `0${m}` }
      if (s < 10) { s = `0${s}` }
      this.time = `${h}:${m}:${s}`
      var t = setTimeout(this.updateTime, 500)
    }
  },
  created: function () {
    this.fetchLinks('links.json'),
    this.updateTime()
  }
})
