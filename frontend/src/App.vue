<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Gamepad2, Search, Sparkles, Layers3, ArrowRight, Zap, Clock3, Activity, ChevronDown, X, Github, Menu, AlertCircle, LoaderCircle, Check, Info } from 'lucide-vue-next'
const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const query = ref('')
const games = ref([])
const total = ref(0)
const selected = ref(null)
const suggestionsOpen = ref(false)
const loadingGames = ref(false)
const loadingResults = ref(false)
const results = ref(null)
const error = ref('')
const searchError = ref('')
const k = ref(6)
const activeTab = ref('all')
let requestNumber = 0
const fmt = n => typeof n === 'number' ? `${Math.round(n * 100)}%` : '—'
const image = game => game?.image && /^https?:\/\//.test(game.image) ? game.image : ''
const score = game => typeof game?.score === 'number' ? Math.round(game.score * 100) : 0
const displayed = computed(() => results.value?.results?.slice(0, k.value) || [])
async function searchGames() {
  const req = ++requestNumber
  loadingGames.value = true
  searchError.value = ''
  try {
    const r = await fetch(`${API}/api/games?search=${encodeURIComponent(query.value)}&limit=18`)
    if (!r.ok) throw new Error('Impossible de récupérer les jeux')
    const data = await r.json()
    if (req === requestNumber) { games.value = data.items || []; total.value = data.total || 0 }
  } catch (e) { if (req === requestNumber) searchError.value = 'API inaccessible. Démarre le backend FastAPI.' }
  finally { if (req === requestNumber) loadingGames.value = false }
}
let debounce
watch(query, () => { suggestionsOpen.value = true; clearTimeout(debounce); debounce = setTimeout(searchGames, 240) })
onMounted(searchGames)
function choose(game) { selected.value = game; query.value = game.title; suggestionsOpen.value = false; results.value = null; error.value = '' }
function clearSelection() { selected.value = null; results.value = null; query.value = ''; suggestionsOpen.value = true }
async function recommend() {
  if (!selected.value) { suggestionsOpen.value = true; return }
  loadingResults.value = true; error.value = ''; results.value = null
  try {
    const r = await fetch(`${API}/api/recommend/jaccard/${selected.value.id}?k=${k.value}`)
    if (!r.ok) throw new Error(`Erreur HTTP ${r.status}`)
    results.value = await r.json()
    document.getElementById('recommendations')?.scrollIntoView({behavior:'smooth',block:'start'})
  } catch(e) { error.value = `Impossible de charger les recommandations : ${e.message}` }
  finally { loadingResults.value = false }
}
</script>
<template>
<div class="app-shell">
  <header class="header"><div class="header-inner">
    <a class="brand" href="#home"><span class="brand-icon"><Gamepad2 :size="23" :stroke-width="2.6"/></span><span>game<span class="brand-accent">match</span><span class="brand-dot">.</span></span></a>
    <nav><a href="#home" class="nav-active">Découvrir</a><a href="#how">Comment ça marche</a><a href="#recommendations">Recommandations</a></nav>
    <span class="header-pill"><span class="online-dot"></span> Projet BUT 3 · v0.1</span>
  </div></header>
  <main id="home">
    <section class="hero container"><div class="hero-content">
      <div class="eyebrow"><Sparkles :size="14"/> LE MOTEUR DE RECOMMANDATION GAMING <span class="eyebrow-arrow">↗</span></div>
      <h1>Ton prochain <span class="text-gradient">coup de cœur</span><br/>est à un clic.</h1>
      <p class="hero-description">Tu as adoré un jeu ? Trouve ceux qui lui ressemblent vraiment. Deux algorithmes, une seule mission : dénicher ta prochaine obsession.</p>
      <div class="hero-features"><span><Check :size="15"/> 5 000 jeux analysés</span><span><Check :size="15"/> Recommandations intelligentes</span></div>
      <div class="search-panel"><label for="game-search"><Search :size="18"/> RECHERCHE TON JEU PRÉFÉRÉ</label>
        <div class="search-wrap"><Search class="search-icon" :size="21"/><input id="game-search" v-model="query" @focus="suggestionsOpen=true" @keydown.enter.prevent="games.length && choose(games[0])" placeholder="Ex. Elden Ring, Stardew Valley, Hades..." autocomplete="off"/><button v-if="query" class="clear" @click="clearSelection" aria-label="Effacer"><X :size="17"/></button></div>
        <div v-if="suggestionsOpen && (query || searchError)" class="suggestions"><div v-if="loadingGames" class="suggestion-info"><LoaderCircle class="spin" :size="17"/> Recherche en cours...</div><div v-else-if="searchError" class="suggestion-info error-text">{{ searchError }}</div><template v-else><div class="suggestion-heading">{{ total }} jeu{{total>1?'x':''}} trouvé{{total>1?'s':''}}</div><button v-for="game in games" :key="game.id" class="suggestion" @click="choose(game)"><img v-if="image(game)" :src="image(game)" alt="" @error="$event.target.style.display='none'"/><span class="suggestion-title">{{game.title}}</span><ArrowRight :size="15"/></button><div v-if="!games.length" class="suggestion-info">Aucun jeu trouvé. Essaie un autre titre.</div></template></div>
        <div class="search-footer"><span v-if="selected"><Check :size="15" class="green"/> <strong>{{ selected.title }}</strong> sélectionné</span><span v-else>Sélectionne un jeu pour commencer</span><span class="dataset-label"><span class="online-dot"></span> STEAM DATASET</span></div>
      </div>
      <div class="action-row"><button class="primary-btn" :disabled="loadingResults || !selected" @click="recommend"><LoaderCircle v-if="loadingResults" class="spin" :size="18"/><Sparkles v-else :size="18"/> {{loadingResults?'Analyse en cours...':'Trouver des jeux similaires'}} <ArrowRight :size="18"/></button><div class="count-select"><span>Résultats</span><select v-model.number="k"><option :value="5">5 jeux</option><option :value="6">6 jeux</option><option :value="10">10 jeux</option></select><ChevronDown :size="14"/></div></div>
    </div><div class="hero-art" aria-hidden="true"><div class="art-glow"></div><div class="art-orbit orbit-1"></div><div class="art-orbit orbit-2"></div><div class="art-card card-back"><div class="fake-art art-purple"><Gamepad2 :size="70"/></div><div class="fake-lines"><span></span><span></span></div></div><div class="art-card card-front"><div class="fake-art art-blue"><Gamepad2 :size="100"/></div><div class="fake-card-footer"><div><span class="fake-title">DISCOVER MORE</span><small>Explore. Compare. Play.</small></div><span class="fake-arrow">↗</span></div></div><div class="floating-badge badge-top"><Sparkles :size="17"/> Smart picks</div><div class="floating-badge badge-bottom"><Zap :size="17"/> Powered by data</div></div></section>
    <section class="stats container"><div><span class="stat-number">5 000<span>+</span></span><span class="stat-label">JEUX DANS LE CATALOGUE</span></div><div><span class="stat-number">2<span>×</span></span><span class="stat-label">MÉTHODES À COMPARER</span></div><div><span class="stat-number">100<span>%</span></span><span class="stat-label">BASÉ SUR LES DONNÉES</span></div></section>
    <section id="recommendations" class="results-section container"><div class="section-heading"><div><div class="section-kicker">/ TES DÉCOUVERTES</div><h2>Des jeux faits <span class="text-gradient">pour toi.</span></h2><p>Les recommandations sont calculées à partir des tags des jeux Steam.</p></div><div v-if="results" class="result-count">{{ displayed.length }} recommandations</div></div>
      <div v-if="error" class="error-banner"><AlertCircle :size="19"/> {{error}}</div>
      <div v-if="!results && !loadingResults" class="empty-state"><div class="empty-icon"><Gamepad2 :size="36"/></div><h3>La prochaine aventure t'attend</h3><p>Choisis ton jeu préféré ci-dessus et lance l'analyse pour découvrir des jeux similaires.</p></div>
      <div v-if="loadingResults" class="empty-state"><LoaderCircle :size="35" class="spin accent-icon"/><h3>On cherche tes prochains favoris...</h3><p>Comparaison des tags en cours.</p></div>
      <template v-if="results"><div class="results-toolbar"><div class="method-chip"><span class="method-dot"></span> Similarité de Jaccard</div><div class="source-chip">À partir de <strong>{{results.source}}</strong></div></div><div class="game-grid"><article v-for="(game,index) in displayed" :key="game.id" class="game-card"><div class="game-image"><img v-if="image(game)" :src="image(game)" :alt="game.title" loading="lazy" @error="$event.target.style.display='none'"/><Gamepad2 class="fallback-icon" :size="48"/><span class="rank">#{{String(index+1).padStart(2,'0')}}</span></div><div class="game-info"><div class="score-row"><span class="similarity-label">SIMILARITÉ</span><span class="score-value">{{fmt(game.score)}}</span></div><div class="score-track"><div :style="{width:score(game)+'%'}"></div></div><h3 :title="game.title">{{game.title}}</h3><p class="genre">{{game.genres || 'Jeu vidéo'}}</p></div></article></div>
      <div class="metrics-bar"><div><Clock3 :size="20"/><span><strong>{{results.metrics?.time_ms ?? '—'}} ms</strong><small>Temps d'exécution</small></span></div><div><Layers3 :size="20"/><span><strong>{{results.metrics?.compared ?? '—'}}</strong><small>Jeux comparés</small></span></div><div><Activity :size="20"/><span><strong>Jaccard</strong><small>Algorithme utilisé</small></span></div></div></template>
    </section>
    <section id="how" class="how-section"><div class="container"><div class="section-kicker">/ SOUS LE CAPOT</div><h2>Deux approches. <span class="text-gradient">Un seul objectif.</span></h2><p class="how-intro">GameMatch compare deux façons de trouver des jeux similaires, avec des résultats et performances mesurables.</p><div class="methods-grid"><div class="method-card"><div class="method-header"><span class="method-icon"><Layers3 :size="23"/></span><span class="status status-live"><span class="online-dot"></span> DISPONIBLE</span></div><span class="method-index">MÉTHODE 01</span><h3>Similarité de Jaccard</h3><p>Compare les tags associés aux jeux pour identifier ceux qui partagent le plus de caractéristiques.</p><div class="method-footer"><span>Basé sur les tags</span><ArrowRight :size="18"/></div></div><div class="method-card"><div class="method-header"><span class="method-icon ai-icon"><Sparkles :size="23"/></span><span class="status status-soon">BIENTÔT DISPONIBLE</span></div><span class="method-index">MÉTHODE 02</span><h3>Embeddings sémantiques</h3><p>Analyse le sens des descriptions avec un modèle d'IA pour repérer les jeux proches sémantiquement.</p><div class="method-footer"><span>Sentence Transformers · IA</span><ArrowRight :size="18"/></div></div></div><div class="note"><Info :size="17"/> Le dashboard comparatif complet (temps, mémoire, énergie) sera disponible lorsque les deux méthodes seront intégrées.</div></div></section>
  </main><footer><div class="container footer-inner"><div class="brand footer-brand"><span class="brand-icon"><Gamepad2 :size="19"/></span><span>game<span class="brand-accent">match</span><span class="brand-dot">.</span></span></div><span>Projet SAÉ 5.Real.01 · BUT 3 Informatique · Les Castors bâtisseurs</span><span>Fait avec Vue 3 + FastAPI</span></div></footer>
</div>
</template>
