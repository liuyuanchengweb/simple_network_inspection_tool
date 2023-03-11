import packageData from '../package.json'

export default [
  {
    url: '/api/getFuncList',
    method: 'get',
    response: () => {
      return {
        code: 0,
        message: 'ok',
        data: packageData,
      }
    },
  },
]
