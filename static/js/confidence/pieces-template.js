var data = {
    rects: [],
    current: {},
  }
  Vue.component('pieces', {
    props: ['stats', 'imageurl', 'width', 'height', 'current'],
    template: '#pieces-template',
    delimiters: ['[[', ']]'],
    components: {
      // a sub component for the labels
      'split-box': {
        props:  ['stat', 'index', 'total', 'choice', 'keyaction'],
        template: '#split-box-template',
        data: function() { 
          return data;
        },
        computed: {
          // Color 1 Added, 2 Modified.
          strokeColor: function() {
            if (this.stat.op == 3){
              return "white"
            } else if (this.stat.selected) {
              return "red"
            } else if (this.stat.op == 1){
              return "yellow"
            }
            else if (this.stat.op == 0){
              return "blue"
            } else if (this.stat.op == 2){
              return "green"
            }
          },
          
        }
      }
    },
    computed: {
      current_img_datauri: function() {
        var current = this.current;
        if (current == undefined)
        {
          return null;
        }
        window.preview_image = getImagePortion(window.vv.image, current.width, current.height, current.x, current.y, 1);
        return  window.preview_image;
      },
      viewbox: function() {
            return [this.current_x, 0, this.current_width, this.height].join(' ')
      },
      current_x: function() {
        if (this.current == null) {
          return 0;
        }
        return this.mean_x - _.meanBy(this.rects, 'width')*1.5;
      },
      mean_x: function() {
        return _.meanBy(this.rects, 'x');
      },
      current_width: function() {
        if (this.current === null) {
          return 0;
        }
        return _.meanBy(this.rects, 'width') * 3.5;
      },
      current_line_no: function() {
        if (this.current === null) {
          return 0;
        }
        return this.current.line_no;
      },
      rects: function() {
        return _.sortBy(_.filter(this.stats, { line_no: this.current_line_no}), ['y']);
      }
    },
    created() {
      this.$on('resize', this.update_rect);
      this.$on('drag', this.drag_rect);
      this.$on('resizend', this.actionend);
      this.$on('dragend', this.actionend);
      var that = this;
      document.addEventListener('keyup', this.keyaction);
      interact('.resize-drag')
      .resizable({
          edges: { left: true, right: true, bottom: true, top: true },
          onend:  function (event) {
            //window.vv.$emit('resizend', event)
            that.actionend(event)
          }
      })
      .on('resizemove',function (event) {
         //window.vv.$emit('resize', event)
         that.update_rect(event)
      })
      .draggable({
          // enable inertial throwing
          inertia: true,
          // keep the element within the area of it's parent
          restrict: {
              restriction: "parent",
              endOnly: true,
              elementRect: { top: 0, left: 0, bottom: 1, right: 1 }
          },
  
          // call this function on every dragmove event
          onmove: function (event) {
              //window.vv.$emit('drag', event)
              that.drag_rect(event)
          },
          // call this function on every dragend event
          onend: function (event) {
              //window.vv.$emit('dragend', event)
              that.actionend(event)
          }
      });
    },
    beforeDestroy() {
      document.removeEventListener('keyup', this.keyaction)
    },
    methods: {
      remove: function (rect) {
        var django_api = "/api/rects/"+rect.id;
        var index = this.stats.indexOf(rect);
        this.$http.delete(django_api).then(function (response) {
              // success callback
              //删除显示图片，删除删格背景数据
              Vue.delete(vv.render_stats, _.findIndex(vv.render_stats, {id: rect.id}));
              Vue.delete(vv.stats, _.findIndex(vv.stats, {id: rect.id}));
              this.choice(this.rects[0]);
          }, function(error) {
            // error callback
            console.log('Fail，网址或相关错误！\n错误码：' + error.status + "\n结果：" + error.ok);
          });
       
      },
      add_new: function() {
        this.add_rect(null);
      },
      add_rect: function(event){
        if (event){
          var post_data = { line_no: this.current_line_no, x: event.offsetX, y: event.offsetY, width: 30, height: 30, op: 0, confidence: 1, page_id: vv.page_id, hans: 'N' };
        } else {
          var post_data = { line_no: this.current_line_no, x: this.current.x + 30, y: this.current.y + 30, width: 30, height: 30, op: 0, confidence: 1, page_id: vv.page_id, hans: 'N' };
        }
        var django_api = "/api/rects"//本地接口
        this.$http.post(django_api, post_data).then(function (response) {
            // success callback
            //this.image_url = response.data.image_url;
            post_data.id = response.data.id;
            post_data.line_no = this.current_line_no;
            post_data.selected = true;
            this.stats.push(post_data);
            vv.stats.push(post_data);
            vv.render_stats.push(post_data);
            this.$nextTick(function(){
              this.choice(post_data);
            })
        }, function(error) {
          // error callback
          console.log('Fail，网址或相关错误！\n错误码：' + error.status + "\n结果：" + error.ok);
        });
      },
      gonext: function (){
        var loc = this.rects.indexOf(this.current);
        var next = this.rects[loc+1];
        if (next) {
          this.choice(next)
        }
      },
      sync_current: function () {
        vv.current = this.current;
        Vue.set(vv.stats, _.findIndex(vv.stats, {id: this.current.id}), this.current);
        var _idx = _.findIndex(vv.render_stats, {id: this.current.id});
        vv.render_stats[_idx].op = this.current.op
        Vue.set(vv.render_stats, _idx, vv.render_stats[_idx]);
      },
      goprev: function() {
        var loc = this.rects.indexOf(this.current);
        var prev = this.rects[loc-1];
        if (prev) {
          this.choice(prev)
        }
      },
        keyaction: function(ev){
          var current = this.current;
          //var index = this.stats.indexOf(this.current);
          console.log(ev.keyCode);
          // 8 delete
          // 13 return
          if (ev.keyCode == 8) //delete
          {
            this.remove(current);
          } else if (ev.keyCode == 13){
            current.x -= 2;
            current.y -= 2;
            current.width += 4;
            current.height += 4;
            this.normalize_current();
            current.op = 2;
            this.sync_current();
            this.actionend(0)
          } else if (ev.keyCode == 38) //up
          {
            this.goprev()
          } else if (ev.keyCode == 40) //down
          {
            this.gonext()
          } else if (ev.keyCode == 37) //left
          {
            current.x -= 2;
            this.normalize_current();
            current.op = 2;
            this.sync_current();
            this.actionend(0)
          } else if (ev.keyCode == 39) //right
          {
            current.y -= 2;
            this.normalize_current();
            current.op = 2;
            this.sync_current();
            this.actionend(0)
          }
        },
        unselect: function () {
          this.stats = _.map(this.stats, function(rect) { rect.selected = false;return rect});  
        },
        choice: function(stat) {
          var index = _.findIndex(this.stats, {id: stat.id});
          this.unselect();
          this.current = this.stats[index]
          this.current.selected = true;
          Vue.set(this.stats, index, this.current);
        },
          normalize_current: function(){
            if (this.current.x < 0) {
              this.current.x = 0
            }
            if (this.current.x > this.width) {
              this.current.x = this.width;
            }
            if (this.current.y < 0) {
              this.current.y = 0
            }
            if (this.current.y > this.height) {
              this.current.y = this.height;
            }

          },
          update_rect:  function(event){
            console.log('update_rect');
            var index = this.stats.indexOf(this.current);
            var target = event.target,
            x = (this.current.x  || 0),
            y = (this.current.y || 0);
      
            // update the element's style
            if ((event.rect.width > 2) && (event.rect.height >2)) {
              this.current.width = parseInt(event.rect.width) ;
              this.current.height = parseInt(event.rect.height) ;
            }
      
      
            // translate when resizing from top or left edges
            console.log(event.deltaRect.left, event.deltaRect.top)
            console.log(event.dx, event.dy)
            x += event.deltaRect.left;
            y += event.deltaRect.top;
      
            this.current.x = parseInt(x);
            this.current.y = parseInt(y);
            this.normalize_current();

            this.current.op = 2;
            this.sync_current()
            //Vue.set(this.stats, index, this.current);
      
          },
          drag_rect: function(event) {
            console.log('drag_rect');
            var target = event.target,
            x = (this.current.x  || 0),
            y = (this.current.y || 0);
      
            // translate when resizing from top or left edges
            x += event.dx;
            y += event.dy;
      
      
            this.current.x = parseInt(x);
            this.current.y = parseInt(y);
            this.current.op = 2;
            this.normalize_current();
            this.sync_current()
            //Vue.set(this.rects, this.index, this.current);
          },
          actionend: function(event) {
            
            var django_api = "/api/rects/" + this.current.id;//本地接口
            var post_data = {id: this.current.id, x: this.current.x , y: this.current.y, width: this.current.width, height: this.current.height, op: this.current.op}
            this.$http.put(django_api, post_data).then(function (response) {
                // success callback
                //this.image_url = response.data.image_url;
                
                console.log("end", this.current.x , this.current.y, this.current.width, this.current.height )
            }, function(error) {
              // error callback
              console.log('Fail，网址或相关错误！\n错误码：' + error.status + "\n结果：" + error.ok);
            });
            
          }
    }
  });