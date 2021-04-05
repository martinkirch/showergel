<template>
  <div class="content">
    <h1>This is Showergel</h1>
    <h2>A companion app for your Liquidsoap radio</h2>
    <p>Version {{ parameters.version }}</p>
    <p>Showergel is still in early development.</p>
    <ul>
      <li>
        <a href="https://showergel.readthedocs.io/en/latest/" target="_blank">
          Documentation
        </a>
      </li>
      <li>
        <a href="https://www.liquidsoap.info/doc-1.4.4/" target="_blank">
          Liquidsoap documentation
        </a>
      </li>
      <li>
        <a href="https://github.com/martinkirch/showergel" target="_blank">
          Sources and issue tracker
        </a>
      </li>
    </ul>
  </div>
</template>


<script>
export default {
  props: ['parameters']
}
</script>
