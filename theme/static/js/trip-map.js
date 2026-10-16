const PALETTE = getComputedStyle(document.documentElement);
const color = (name) => PALETTE.getPropertyValue(name).trim();
const MARKER_COLOR = color('--color-accent');
const MAP_COLORS = [
  ['background', 'background-color', color('--color-map-land')],
  ['water', 'fill-color', color('--color-map-water')],
  ['waterway', 'line-color', color('--color-map-water')],
];

function groupByPlace(trips) {
  const places = new Map();
  for (const trip of trips.filter((trip) => trip.coords)) {
    const key = trip.coords.join(',');
    if (!places.has(key)) {
      places.set(key, { location: trip.location, coords: trip.coords, trips: [] });
    }
    places.get(key).trips.push(trip);
  }
  return [...places.values()];
}

function popupContent(place) {
  const heading = document.createElement('strong');
  heading.textContent = place.location;

  const list = document.createElement('ul');
  for (const trip of place.trips) {
    const item = document.createElement('li');
    item.textContent = `${trip.dates}: ${trip.event}`;
    list.append(item);
  }

  const content = document.createElement('div');
  content.append(heading, list);
  return content;
}

function lngLat(place) {
  return [place.coords[1], place.coords[0]];
}

function renderTripMap(element) {
  const places = groupByPlace(JSON.parse(element.dataset.trips));
  if (!places.length) return;

  const bounds = new maplibregl.LngLatBounds();
  places.forEach((place) => bounds.extend(lngLat(place)));

  const map = new maplibregl.Map({
    container: element,
    style: element.dataset.style,
    bounds,
    fitBoundsOptions: { padding: 48, maxZoom: 6 },
    cooperativeGestures: true,
    attributionControl: { compact: true },
  });
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }));
  map.once('load', () => map.fire('drag'));
  map.on('style.load', () => {
    for (const [layer, property, value] of MAP_COLORS) {
      if (map.getLayer(layer)) map.setPaintProperty(layer, property, value);
    }
  });

  for (const place of places) {
    const popup = new maplibregl.Popup({ offset: 28, closeButton: false }).setDOMContent(popupContent(place));
    new maplibregl.Marker({ color: MARKER_COLOR }).setLngLat(lngLat(place)).setPopup(popup).addTo(map);
  }
}

document.querySelectorAll('.trip-map').forEach(renderTripMap);
