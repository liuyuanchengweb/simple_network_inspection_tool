/**
 * 
 * @param {*} timestamp 时间戳 单位毫秒
 * @param {*} formats 格式 1. Y-m-d 2. Y-m-d H:i:s 3. Y年m月d日 4. Y年m月d日 H时i分
 * @returns 返回与formats匹配的时间格式字符串
 */
export const dateFormat = (timestamp, formats) => {
  timestamp = timestamp || new Date().getTime()
  formats = formats || 'Y-m-d'

  var zero = function (value) {
    if (value < 10) {
      return '0' + value
    }
    return value
  }
  var myDate = timestamp ? new Date(timestamp) : new Date()

  var year = myDate.getFullYear()
  var month = zero(myDate.getMonth() + 1)
  var day = zero(myDate.getDate())
  var hour = zero(myDate.getHours())
  var minite = zero(myDate.getMinutes())
  var second = zero(myDate.getSeconds())

  return formats.replace(/Y|m|d|H|i|s/gi, function (matches) {
    return {
      Y: year,
      m: month,
      d: day,
      H: hour,
      i: minite,
      s: second,
    }[matches]
  })
}

/**
 * 
 * @param {*} second 时间戳 单位秒
 * @returns `${day}天${hour}小时${minute}分${seconds}秒`
 */
export const dateCalculation = function (second) {
  if (second > 0) {
    var day = 0
    var hour = 0
    var minute = 0
    var seconds = 0
    var data = {}
    minute = Math.floor(second / 60)
    seconds = (second % 60).toFixed(0)
    if (parseInt(minute) > 60) {
      hour = parseInt(minute / 60)
      minute %= 60 //算出有多分钟
    }
    if (parseInt(hour) > 24) {
      day = parseInt(hour / 24)
      hour %= 24 //算出有多分钟
    }
    data.day = day
    data.hour = hour
    data.minute = minute
    return `${day}天${hour}小时${minute}分${seconds}秒`
  }
}
