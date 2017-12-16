function getCookie(name) {
  let arr,
      reg=new RegExp("(^| )"+name+"=([^;]*)(;|$)")
  if(arr=document.cookie.match(reg)) {
    return decodeURIComponent(arr[2])
  }
}

// 设置 POST 请求时 的 data 格式
//Vue.http.options.emulateJSON = true

// 设置 X-CSRFToken
Vue.http.interceptors.push(function(request, next) {
  //request.method = 'POST'
  request.headers.set('X-CSRFToken', getCookie('csrftoken'))
  next()
})

window.vv=new Vue({
    el: '#split-rects',
    delimiters: ['[[', ']]'],
    data: {
      newLabel: '',
      stats: [],
      render_stats: [],
      api_base: "/api/rects/one/list",
      current_id: 0,
      current: null,
      image_url: '',
      height: 1,
      width: 1,
      page_id: '',
      image: null
    },
    mounted: function() {
      var that = this;
      $('.modal').modal({
          dismissible: true, // Modal can be dismissed by clicking outside of the modal
          opacity: .5, // Opacity of modal background
          inDuration: 300, // Transition in duration
          outDuration: 200, // Transition out duration
          startingTop: '4%', // Starting top style attribute
          endingTop: '10%', // Ending top style attribute
          ready: function(modal, trigger) { // Callback for Modal open. Modal and trigger parameters available.
            that.$children[0].choice(that.current); 
          },
          complete: function() { vv.reload_render_stats(); } // Callback for Modal close
        }
      );
      this.loadRects();
      window.ps = new PerfectScrollbar("body");
    },
    computed: {
      rects: function() {
        return _.sortBy(_.filter(this.stats, { op: 0 }), ['confidence']);   
      },
      same_line_rects: function() {
        if (!this.current)
          return []
        return _.filter(this.stats, {line_no: this.current.line_no })
      },
      done_stats: function() {
        return _.reject(this.stats,{op: 0});
      },
    },
    methods: {
      loadRects: function() {
          var json_server_api = this.api_base;
          this.$http.get(json_server_api).then(function (response) {
              this.stats = response.data.models;
              this.stats = _.map(this.stats, function(rect) { return _.assign({selected: false}, rect) });
              this.image_url = response.data.image_url;
              this.page_id = response.data.page_id;
              this.onimage_loaded();
          }, function(error) {
            // error callback
            console.log('Fail，网址或相关错误！\n错误码：' + error.status + "\n结果：" + error.ok);
          });
      },
      onimage_loaded: function () {
        var image = new Image();
        image.crossOrigin = "Anonymous";
        var that = this;
        image.onload = function(){
          that.update_embed_img(image);
          that.height = image.height;
          that.width = image.width;
        };
        image.src = this.image_url;
        this.image = image;
      },
      update_embed_img: function(new_image) {
        this.render_stats = _.map(this.rects, function(rect) { return _.assign({selected: false, embed_inset: getImagePortion(new_image, rect.width, rect.height, rect.x, rect.y, 1)}, rect);});        
        this.$nextTick(function(){
                var containerBlog = $("#item-posts");
                containerBlog.imagesLoaded(function() {
                  containerBlog.masonry({
                    itemSelector: ".item",
                    columnWidth: ".item-sizer-small",
                  });
                  window.ps.update()
              })})
      },
      reload_render_stats: function() {
        this.render_stats = _.filter(this.render_stats, { op: 0 });
        this.$children[0].unselect();                    
      },
      detail_uri: function(rect){
        return "/rects/" + rect.id
      },
      open_modal: function() {
        $('#modal1').modal('open');
      },
      choice: function(stat) {
        index = this.stats.indexOf(stat)
        stat.selected  = true
        this.current = stat
        Vue.set(this.stats, index, stat);
        this.open_modal();
      },
      all_done: function() {
        var django_api = "/api/rects/"+ this.page_id + "/done";//本地接口
        var that = this;
        this.$http.post(django_api, {}).then(function (response) {
          // success callback

          swal({title: "随喜!", text: "成功提交一个校对!正在加载下一页", timer: 2000, showConfirmButton: true});
          that.loadRects();
      }, function(error) {
        // error callback
        swal("稍等!", "出现一个bug!", "error")

      });
      }
    }
  })
  
  $(function() {
  
      $('.lt-menu .menu-content').first().find('.m-submenu').first().addClass('m-active');
  
  });
