var ID = '@id', REV = '@reverse', TYPE = '@type'

function Index(data) {
  var items = data['@graph']
  var self = this
  items.forEach(function (it) { self.indexNode(it) })
  items.forEach(function (it) { self.connectNode(it) })
}
Index.prototype = {

  nodes: [],
  byType: {},
  byId: {},

  indexNode: function (node) {
    this.getItems(this.byType, node[TYPE]).push(node)
    this.byId[node[ID]] = node
  },

  connectNode: function (node) {
    var self = this
    for (key in node) {
      var o = node[key]
      if (typeof o.forEach === 'function') {
        var targets = []
        o.forEach(function (part) {
          var target = self.getConnectedTarget(node, key, part)
          targets.push(target)
        })
        node[key] = targets
      } else {
        var target = this.getConnectedTarget(node, key, o)
        if (target) {
          node[key] = target
        }
      }
    }
    this.nodes.push(node)
  },

  getItems: function (map, key) {
    if (!map[key]) {
      map[key] = []
    }
    return map[key]
  },

  getConnectedTarget: function (node, key, o) {
    var ref = o[ID]
    if (ref === undefined) {
      return o
    }
    var target = this.byId[ref]
    if (target) {
      node[key] = target
      var byRev = target[REV]
      if (!byRev) {
        byRev = target[REV] = {}
      }
      this.getItems(byRev, key).push(node)
    }
    return target
  }

}

if (typeof exports !== 'undefined') {
    exports.Index = Index
    exports.ID = ID
    exports.REV = REV
    exports.TYPE = TYPE
}
