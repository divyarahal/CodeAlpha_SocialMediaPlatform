const csrf = document.querySelector('meta[name="csrf-token"]').content;

async function postJSON(url) {
  const res = await fetch(url, { method: 'POST', headers: { 'X-CSRFToken': csrf } });
  if (res.status === 401) { window.location = '/accounts/login/?next=' + encodeURIComponent(location.pathname); return null; }
  const data = await res.json();
  if (!res.ok) { alert(data.error || 'Something went wrong'); return null; }
  return data;
}

document.addEventListener('click', async (e) => {
  const like = e.target.closest('.like-btn');
  if (like) {
    const data = await postJSON(like.dataset.url);
    if (!data) return;
    like.classList.toggle('liked', data.liked);
    like.querySelector('.heart').textContent = data.liked ? '♥' : '♡';
    like.querySelector('.like-count').textContent = data.count;
    return;
  }
  const follow = e.target.closest('.follow-btn');
  if (follow) {
    const data = await postJSON(follow.dataset.url);
    if (!data) return;
    follow.textContent = data.following ? 'Following' : 'Follow';
    follow.classList.toggle('ghost', data.following);
    const counter = document.getElementById('follower-count');
    if (counter) counter.textContent = data.followers;
  }
});

const box = document.querySelector('.composer textarea');
const chars = document.getElementById('chars');
if (box && chars) box.addEventListener('input', () => { chars.textContent = box.value.length; });
