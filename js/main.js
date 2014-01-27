
window.onload = function () {
  var req = new XMLHttpRequest()
  req.onload = function (evt) {
      var data = JSON.parse(req.responseText)
      start(data)
  }
  req.open("GET", "data/all.json")
  req.send()
}

function start(data) {
    var index = new Index(data)
    init(index)
    animate(1)
}


var sweBox = {top: 69.06, right: 24.155833, bottom: 55.336944, left: 10.9575}
var sliceX = sweBox.right - sweBox.left
var sliceY = sweBox.top - sweBox.bottom

var map = {width: 500, height: 1090}
var offset = {
  x: ((map.width / sliceX) * (180 + sweBox.left)),
  y: ((map.height / sliceY) * (90 - sweBox.top))
}

function toPos(loc) {
  var x = ((map.width / sliceX) * (180 + loc.long))
  var y = ((map.height / sliceY) * (90 - loc.lat))
  return {x: x - offset.x, y: y - offset.y}
}

function createCard(item) {
  var topic = item[REV].primaryTopic
  var loc = item.atLocation
  var html = ""
  var txt = loc.label.str || loc.label
  html += '<p><b>'+ txt  +'</b></p>'
  html += '<div class="info">'
  if (item.qualifiedAssociation)
    item.qualifiedAssociation.forEach(function (assoc) {
      if (assoc.agent.personTitle || assoc.role) {
        var txt = (assoc.agent.personTitle || '') + ' ' + (assoc.role || '')
        html += '<p>'+ txt  +'</p>'
      }
    })
  topic.forEach(function (work) {
    html += '<p>'+ work.title +'<br>'+ work.description +'</p>'
  })
  html += '</div>'
  return html
}

var renderer, camera, scene, floor

//lat: 51.225 - 65.3333
//long: -2.894 - 21.5

function init(index) {
  renderer = new THREE.CSS3DRenderer({antialias: true})
  renderer.setSize(window.innerWidth, window.innerHeight)

  camera = new THREE.PerspectiveCamera(
          75, window.innerWidth / window.innerHeight, 1, 10000)
  camera.position.z = 600

  scene = new THREE.Scene()

  var mapSrc = document.getElementById('map').getAttribute('src')
  var elem = document.createElement('img')
  elem.id = 'floor'
  elem.style.width = map.width + 'px'
  elem.style.height = map.height + 'px'
  elem.src = mapSrc
  floor = new THREE.CSS3DObject(elem)
  scene.add(floor)

  // TODO: loop over each place instead
  index.byType.Activity.forEach(function (item) {
    var loc = item.atLocation
    if (!loc)
      return
    var lat = loc.lat || (loc['geo:lat']? loc['geo:lat'][0].str : null),
        long = loc.long || (loc['geo:long']? loc['geo:long'][0].str : null)
    var topic = item[REV].primaryTopic
    if (!lat || !topic)
      return
    lat = parseFloat(lat)
    long = parseFloat(long)

    var elem = document.createElement('div')
    elem.className = 'place'
    elem.onclick = function () {
      this.classList.toggle('active')
    }

    var html = createCard(item)

    var pos = toPos({lat: lat, long: long})

    elem.innerHTML = html
    var place = new THREE.CSS3DObject(elem)

    place.position.x = pos.x - 200
    place.position.y = 16
    place.position.z = pos.y - 600
    scene.add(place)
  })

  document.body.appendChild(renderer.domElement)

  window.addEventListener('resize', function () {
    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()
    renderer.setSize(window.innerWidth, window.innerHeight)
  }, false)

  document.body.ondblclick = function () {
    running = !running
    animate(1)
  }
}

var running = true

function animate(t) {
  if (running)
    requestAnimationFrame(animate)

  var s = t/4000
  camera.position.x = Math.sin(s) * -20
  camera.position.y = 180
  camera.position.z = 600 + (Math.cos(s) * 100)
  camera.lookAt(scene.position)
  camera.rotation.y += 0.2

  floor.rotation.x = -Math.PI/2

  renderer.render(scene, camera)
}

