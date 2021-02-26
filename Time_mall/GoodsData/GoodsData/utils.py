import json,time,execjs

from collections import OrderedDict

from .pipelines import AdCategory, ContentCategory, Content, FastFdfs

def getGoodsDetailInfo(iid,cookies_dict):
    #蘑菇街数据js解析代码
    js = execjs.compile('''
                            function V(t, e) {
                                    return t(e = {exports: {}}, e.exports),
                                    e.exports
                            }
                            var U = V(function(t) {
                                var i, n;
                                i = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
                                n = {
                                    rotl: function(t, e) {
                                        return t << e | t >>> 32 - e
                                    },
                                    rotr: function(t, e) {
                                        return t << 32 - e | t >>> e
                                    },
                                    endian: function(t) {
                                        if (t.constructor == Number)
                                            return 16711935 & n.rotl(t, 8) | 4278255360 & n.rotl(t, 24);
                                        for (var e = 0; e < t.length; e++)
                                            t[e] = n.endian(t[e]);
                                        return t
                                    },
                                    randomBytes: function(t) {
                                        for (var e = []; 0 < t; t--)
                                            e.push(Math.floor(256 * Math.random()));
                                        return e
                                    },
                                    bytesToWords: function(t) {
                                        for (var e = [], n = 0, o = 0; n < t.length; n++,
                                        o += 8)
                                            e[o >>> 5] |= t[n] << 24 - o % 32;
                                        return e
                                    },
                                    wordsToBytes: function(t) {
                                        for (var e = [], n = 0; n < 32 * t.length; n += 8)
                                            e.push(t[n >>> 5] >>> 24 - n % 32 & 255);
                                        return e
                                    },
                                    bytesToHex: function(t) {
                                        for (var e = [], n = 0; n < t.length; n++)
                                            e.push((t[n] >>> 4).toString(16)),
                                            e.push((15 & t[n]).toString(16));
                                        return e.join("")
                                    },
                                    hexToBytes: function(t) {
                                        for (var e = [], n = 0; n < t.length; n += 2)
                                            e.push(parseInt(t.substr(n, 2), 16));
                                        return e
                                    },
                                    bytesToBase64: function(t) {
                                        for (var e = [], n = 0; n < t.length; n += 3)
                                            for (var o = t[n] << 16 | t[n + 1] << 8 | t[n + 2], r = 0; r < 4; r++)
                                                8 * n + 6 * r <= 8 * t.length ? e.push(i.charAt(o >>> 6 * (3 - r) & 63)) : e.push("=");
                                        return e.join("")
                                    },
                                    base64ToBytes: function(t) {
                                        t = t.replace(/[^A-Z0-9+\/]/gi, "");
                                        for (var e = [], n = 0, o = 0; n < t.length; o = ++n % 4)
                                            0 != o && e.push((i.indexOf(t.charAt(n - 1)) & Math.pow(2, -2 * o + 8) - 1) << 2 * o | i.indexOf(t.charAt(n)) >>> 6 - 2 * o);
                                        return e
                                    }
                                },
                                    t.exports = n
                                }),
                                q = {
                                    utf8: {
                                        stringToBytes: function(t) {
                                            return q.bin.stringToBytes(unescape(encodeURIComponent(t)))
                                        },
                                        bytesToString: function(t) {
                                            return decodeURIComponent(escape(q.bin.bytesToString(t)))
                                        }
                                    },
                                    bin: {
                                        stringToBytes: function(t) {
                                            for (var e = [], n = 0; n < t.length; n++)
                                                e.push(255 & t.charCodeAt(n));
                                            return e
                                        },
                                        bytesToString: function(t) {
                                            for (var e = [], n = 0; n < t.length; n++)
                                                e.push(String.fromCharCode(t[n]));
                                            return e.join("")
                                        }
                                    }
                                },
                                J = q,
                                F = function(t) {
                                    return null != t && (W(t) || "function" == typeof (e = t).readFloatLE && "function" == typeof e.slice && W(e.slice(0, 0)) || !!t._isBuffer);
                                    var e
                                };
                                function W(t) {
                                    return !!t.constructor && "function" == typeof t.constructor.isBuffer && t.constructor.isBuffer(t)
                                }
                                var z = V(function(t) {
                                    var v, g, _, w, b;
                                    v = U,
                                    g = J.utf8,
                                    _ = F,
                                    w = J.bin,
                                    (b = function(t, e) {
                                        t.constructor == String ? t = e && "binary" === e.encoding ? w.stringToBytes(t) : g.stringToBytes(t) : _(t) ? t = Array.prototype.slice.call(t, 0) : Array.isArray(t) || (t = t.toString());
                                        for (var n = v.bytesToWords(t), o = 8 * t.length, r = 1732584193, i = -271733879, s = -1732584194, a = 271733878, u = 0; u < n.length; u++)
                                            n[u] = 16711935 & (n[u] << 8 | n[u] >>> 24) | 4278255360 & (n[u] << 24 | n[u] >>> 8);
                                        n[o >>> 5] |= 128 << o % 32,
                                        n[14 + (o + 64 >>> 9 << 4)] = o;
                                        var c = b._ff
                                          , p = b._gg
                                          , l = b._hh
                                          , h = b._ii;
                                        for (u = 0; u < n.length; u += 16) {
                                            var f = r
                                              , d = i
                                              , y = s
                                              , m = a;
                                            i = h(i = h(i = h(i = h(i = l(i = l(i = l(i = l(i = p(i = p(i = p(i = p(i = c(i = c(i = c(i = c(i, s = c(s, a = c(a, r = c(r, i, s, a, n[u + 0], 7, -680876936), i, s, n[u + 1], 12, -389564586), r, i, n[u + 2], 17, 606105819), a, r, n[u + 3], 22, -1044525330), s = c(s, a = c(a, r = c(r, i, s, a, n[u + 4], 7, -176418897), i, s, n[u + 5], 12, 1200080426), r, i, n[u + 6], 17, -1473231341), a, r, n[u + 7], 22, -45705983), s = c(s, a = c(a, r = c(r, i, s, a, n[u + 8], 7, 1770035416), i, s, n[u + 9], 12, -1958414417), r, i, n[u + 10], 17, -42063), a, r, n[u + 11], 22, -1990404162), s = c(s, a = c(a, r = c(r, i, s, a, n[u + 12], 7, 1804603682), i, s, n[u + 13], 12, -40341101), r, i, n[u + 14], 17, -1502002290), a, r, n[u + 15], 22, 1236535329), s = p(s, a = p(a, r = p(r, i, s, a, n[u + 1], 5, -165796510), i, s, n[u + 6], 9, -1069501632), r, i, n[u + 11], 14, 643717713), a, r, n[u + 0], 20, -373897302), s = p(s, a = p(a, r = p(r, i, s, a, n[u + 5], 5, -701558691), i, s, n[u + 10], 9, 38016083), r, i, n[u + 15], 14, -660478335), a, r, n[u + 4], 20, -405537848), s = p(s, a = p(a, r = p(r, i, s, a, n[u + 9], 5, 568446438), i, s, n[u + 14], 9, -1019803690), r, i, n[u + 3], 14, -187363961), a, r, n[u + 8], 20, 1163531501), s = p(s, a = p(a, r = p(r, i, s, a, n[u + 13], 5, -1444681467), i, s, n[u + 2], 9, -51403784), r, i, n[u + 7], 14, 1735328473), a, r, n[u + 12], 20, -1926607734), s = l(s, a = l(a, r = l(r, i, s, a, n[u + 5], 4, -378558), i, s, n[u + 8], 11, -2022574463), r, i, n[u + 11], 16, 1839030562), a, r, n[u + 14], 23, -35309556), s = l(s, a = l(a, r = l(r, i, s, a, n[u + 1], 4, -1530992060), i, s, n[u + 4], 11, 1272893353), r, i, n[u + 7], 16, -155497632), a, r, n[u + 10], 23, -1094730640), s = l(s, a = l(a, r = l(r, i, s, a, n[u + 13], 4, 681279174), i, s, n[u + 0], 11, -358537222), r, i, n[u + 3], 16, -722521979), a, r, n[u + 6], 23, 76029189), s = l(s, a = l(a, r = l(r, i, s, a, n[u + 9], 4, -640364487), i, s, n[u + 12], 11, -421815835), r, i, n[u + 15], 16, 530742520), a, r, n[u + 2], 23, -995338651), s = h(s, a = h(a, r = h(r, i, s, a, n[u + 0], 6, -198630844), i, s, n[u + 7], 10, 1126891415), r, i, n[u + 14], 15, -1416354905), a, r, n[u + 5], 21, -57434055), s = h(s, a = h(a, r = h(r, i, s, a, n[u + 12], 6, 1700485571), i, s, n[u + 3], 10, -1894986606), r, i, n[u + 10], 15, -1051523), a, r, n[u + 1], 21, -2054922799), s = h(s, a = h(a, r = h(r, i, s, a, n[u + 8], 6, 1873313359), i, s, n[u + 15], 10, -30611744), r, i, n[u + 6], 15, -1560198380), a, r, n[u + 13], 21, 1309151649), s = h(s, a = h(a, r = h(r, i, s, a, n[u + 4], 6, -145523070), i, s, n[u + 11], 10, -1120210379), r, i, n[u + 2], 15, 718787259), a, r, n[u + 9], 21, -343485551),
                                            r = r + f >>> 0,
                                            i = i + d >>> 0,
                                            s = s + y >>> 0,
                                            a = a + m >>> 0
                                        }
                                        return v.endian([r, i, s, a])
                                    }
                                    )._ff = function(t, e, n, o, r, i, s) {
                                        var a = t + (e & n | ~e & o) + (r >>> 0) + s;
                                        return (a << i | a >>> 32 - i) + e
                                    },
                                    b._gg = function(t, e, n, o, r, i, s) {
                                        var a = t + (e & o | n & ~o) + (r >>> 0) + s;
                                        return (a << i | a >>> 32 - i) + e
                                    },
                                    b._hh = function(t, e, n, o, r, i, s) {
                                        var a = t + (e ^ n ^ o) + (r >>> 0) + s;
                                        return (a << i | a >>> 32 - i) + e
                                    },
                                    b._ii = function(t, e, n, o, r, i, s) {
                                        var a = t + (n ^ (e | ~o)) + (r >>> 0) + s;
                                        return (a << i | a >>> 32 - i) + e
                                    },
                                    b._blocksize = 16,
                                    b._digestsize = 16,
                                    t.exports = function(t, e) {
                                        if (null == t)
                                            throw new Error("Illegal argument " + t);
                                        var n = v.wordsToBytes(b(t, e));
                                        return e && e.asBytes ? n : e && e.asString ? w.bytesToString(n) : v.bytesToHex(n)
                                    }
                                })
                        ''')
    #保证json反序列化后字典键值顺序不发生改变
    content = OrderedDict()
    content['iid'] = iid
    content['activityId'] = ''
    content['fastbuyId'] = ''
    content['template'] = '1-1-detail_normal-1.0.0'
    data_json = json.dumps(content)
    #取出空格----必须去除，我在这里可弄了半天
    data = data_json.replace(' ', '')
    res = js.call('z', data)
    appkey = '100028'
    mw_h5_os = 'unknown'
    mw_t = str(int(time.time() * 1000))
    ttid = 'NMMain@mgj_pc_1.0'
    uuid = cookies_dict.get('__mgjuuid')
    api = 'http.detail.api'
    token = cookies_dict.get('_mwp_h5_token')
    sign_list = []
    sign_list.append(appkey)
    sign_list.append(mw_h5_os)
    sign_list.append(mw_t)
    sign_list.append(ttid)
    sign_list.append(uuid)
    sign_list.append(api)
    sign_list.append('1')
    sign_list.append(res)
    sign_list.append(token)
    sign = '&'.join(sign_list)
    mw_sign = js.call('z', sign)
    url = 'https://api.mogu.com/h5/http.detail.api/1/?data=%7B%22iid%22%3A%22' + iid + '%22%2C%22activityId%22%3A%22%22%2C%22fastbuyId%22%3A%22%22%2C%22template%22%3A%221-1-detail_normal-1.0.0%22%7D&mw-appkey=100028&mw-ttid=NMMain%40mgj_pc_1.0&mw-t=' + mw_t + '&mw-uuid=' + uuid + '&mw-h5-os=unknown&mw-sign=' + mw_sign + '&callback=mwpCb2/'
    return url

def writeDataBase(name,title,pid,link,image,index,price,discountprice=None,category_title=None):
    name1 = name
    name = name[0:name.find(' ')+1]
    #将目录标题统一（男装   男装 推荐  ===>男装）
    if not name:
        name = name1
    # --------------------AdCategory查
    msg = AdCategory().select(name)
    #数据库存在就不插入
    if not msg:
        # --------------------AdCategory表
        AdCategory().insert(name)
        # --------------------AdCategory查
        msg = AdCategory().select(name)
    if msg:#不存在插入
        if msg[0]:
            adCategory_id = msg[0]
            # --------------------ContentCategory查
            msg = ContentCategory().select(pid)
            if not msg:
                if category_title:
                    # --------------ContentCategory表
                    ContentCategory().insert(category_title, pid,
                                             adCategory_id)
                    # --------------------ContentCategory查
                    msg = ContentCategory().select(pid)
                else:
                    # --------------ContentCategory表
                    ContentCategory().insert(name1, pid,
                                     adCategory_id)
                    # --------------------ContentCategory查
                    msg = ContentCategory().select(pid)
            if msg:
                if msg[0]:
                    category_id = msg[0]
                    # ----------------------Content表
                    Content().insert(title, link, image, index, 1, category_id,
                                 price,discountprice)

def verdict(goods,title,link,pid,image,index,price):
    try:
        link = 'https:' + link
    except:
        link = None
    if pid == '138852':
        # print('母装&儿童', pid, goods.get('title'))
        if link:
            category_title = '热门品牌'
            link = goods.get('link')
            writeDataBase('目录', title, pid, link, image, index - 1, price, category_title=category_title)
    elif pid == '138851':
        if link:
            category_title = '流行话题'
            link = goods.get('link')
            writeDataBase('目录', title, pid, link, image, index - 1, price, category_title=category_title)
    elif pid == '132244':
        if link:
            category_title = '主题市场'
            link = goods.get('link')
            writeDataBase('目录', title, pid, link, image, index - 1, price, category_title=category_title)
    elif pid == '110542':
        writeDataBase('母装&儿童', title, pid, link, image, index, price)
    elif pid == '110847':
        writeDataBase('母装&儿童 推荐', title, pid, link, image, index, price)
    elif pid == '110845':
        writeDataBase('家纺&家饰', title, pid, link, image, index, price)
    elif pid == '110538':
        writeDataBase('家纺&家饰 推荐', title, pid, link, image, index, price)
    elif pid == '110759':
        writeDataBase('男装&男鞋', title, pid, link, image, index, price)
    elif pid == '110528':
        writeDataBase('男装&男鞋 推荐', title, pid, link, image, index, price)
    elif pid == '110843':
        writeDataBase('内衣', title, pid, link, image, index, price)
    elif pid == '110535':
        writeDataBase('内衣 推荐', title, pid, link, image, index, price)
    elif pid == '110892':
        writeDataBase('女鞋&包包 推荐', title, pid, link, image, index, price)
    elif pid == '110523' or pid == '110521':
        writeDataBase('女鞋&包包', title, '110523', link, image, index, price)
    elif pid == '110564':
        writeDataBase('女装', title, pid, link, image, index, price)
    elif pid == '110468':
        writeDataBase('限时抢购', title, pid, link, image, index, price)