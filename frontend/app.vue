<template>
  <NuxtLayout>
    <NuxtRouteAnnouncer />
    <NuxtPage :key="$route.fullPath" />
  </NuxtLayout>
</template>