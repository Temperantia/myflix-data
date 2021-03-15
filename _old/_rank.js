const admin = require('firebase-admin');
const serviceAccount = require('./my-flix-91e46-firebase-adminsdk-tx9sq-c48bb4e2a9.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://my-flix-91e46.firebaseio.com',
});
const db = admin.firestore();

async function rank() {
  const videos = (await db.collection('videos').limit(10).get()).docs;
  for (const video of videos) {
    const data = video.data();
    const scores = Object.values(data.scores);
    video.score = scores.reduce((a, b) => a + b) / scores.length;
  }

  videos.sort((a, b) => {
    return a.score <= b.score ? 1 : -1;
  });

  const ranks = {};
  for (const [index, video] of videos) {
    ranks[video.id] = index;
  }
  db.collection('ranks')
    .doc(1)
    .update(ranks);
}

rank();
