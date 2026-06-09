output "namespace" {
  value = kubernetes_namespace.library.metadata[0].name
}