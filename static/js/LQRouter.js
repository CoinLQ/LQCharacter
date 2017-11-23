/**
 * 单页面程序的路由
 */
function LQRouter(config){
    var self = window.LQRouter =  this;
    var defaultConfig = {
        contentSelector: '',//页面内容区域选择器
        navSelector: '',//标题导航区域选择器
        beforeUpdate: function(page){
            //页面切换前执行回调
        },
        afterUpdate: function(page){
            //页面切换后执行回调
        },
        showLoading: function () {
            //加载进度框
        },
        hideLoading: function () {
            //隐藏加载框
        },
        home: {//home页配置
            url: '/site/index',
            title: '',
            catalog: '首页'
        }
    }

    //一个页面路由的数据
    function LQRouterPage(url, title, catalog){
        this.url = url;
        this.title = title;
        this.catalog = catalog;
    }

    //更新导航
    function updateNav(){
        var rootIndex = self.pageStack.length-1;
        while(rootIndex>=0 && self.pageStack[rootIndex].catalog==""){
            rootIndex--;
        }
        $(self.navSelector).empty();
        if(rootIndex>=0){
            while (rootIndex<self.pageStack.length){
                var page = self.pageStack[rootIndex];
                if(page.catalog!=""){
                    $(self.navSelector).append("<span>"+page.catalog+"</span>");
                }
                if(page.title && page.title!=""){
                    $(self.navSelector).append('&gt;');
                    var nav = $("<span>"+page.title+"</span>");
                    nav.data("index", rootIndex);
                    if(rootIndex<self.pageStack.length-1){
                        nav.addClass('nav-title');
                        nav.click(function(){
                            var idx = $(this).data("index");
                            history.go(idx-self.pageStack.length+1);
                        });
                    }
                    $(self.navSelector).append(nav);
                }
                rootIndex++;
            }
        }
    }

    config = $.extend({}, defaultConfig, config);
    this.contentSelector = config.contentSelector;
    this.navSelector = config.navSelector;
    this.beforeUpdate = config.beforeUpdate;
    this.afterUpdate = config.afterUpdate;
    this.showLoading = config.showLoading;
    this.hideLoading = config.hideLoading;
    this.pageStack = [];
    var homePage = new LQRouterPage(config.home.url, config.home.title, config.home.catalog);
    homePage.index = 0;
    this.pageStack.push(homePage);
    history.replaceState(homePage, "", "");

    //跳转到某个页面， url：页面url,  title:导航栏标题， catalog:位于哪个一级菜单下，一级菜单下的首个页面必须传，后续页面必须不传
    this.push = function(url, title, catalog){
        var page = new LQRouterPage(url, title, catalog?catalog:"");
        page.index = self.pageStack.length;
        if(self.showLoading) self.showLoading();
        history.pushState(page, "", "#"+url);
        self.pageStack.push(page);
        updateNav();
        $.post(url, function(data, textStatus, xhr){
            if(self.hideLoading) self.hideLoading();
            try{
                var obj = eval('(' + xhr.responseText + ')');
                if(obj.code==-9999){
                    //showSysTip(obj.msg);
                    return;
                }
            }catch(e){}
            if(self.beforeUpdate) self.beforeUpdate(page);
            $(self.contentSelector).html(data);
            if(self.afterUpdate) self.afterUpdate(page);
        });
    }

    //弹出一个页面，返回上一页
    this.pop = function(){
        history.back();
    }

    window.addEventListener("popstate", function() {
        var page = history.state;
        if(self.showLoading) self.showLoading();
        var curIndex = page.index;
        self.pageStack.splice(curIndex+1, self.pageStack.length-curIndex);
        updateNav();
        $.post(page.url, function(data){
            if(self.hideLoading) self.hideLoading();
            if(self.beforeUpdate) self.beforeUpdate(page);
            $(self.contentSelector).html(data);
            if(self.afterUpdate) self.afterUpdate(page);
        });
    });

    return this;
}

