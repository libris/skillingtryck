var glue = require('./glue'), Index = glue.Index, REV = glue.REV

var data = require('../data/all.json')

var index = new Index(data)

index.byType.Activity.forEach(function (item) {
  var loc = item.atLocation
  if (loc)
    console.log(loc.label, loc.lat, loc.long)
  if (item.qualifiedAssociation)
    item.qualifiedAssociation.forEach(function (assoc) {
      console.log(assoc.agent.personTitle, assoc.role)
    })
  if (item[REV].primaryTopic)
    item[REV].primaryTopic.forEach(function (work) {
      console.log(work.title, '--', work.description)
    })
  console.log()
})

//lat: 51.225 - 65.3333
//long: -2.894 - 21.5
