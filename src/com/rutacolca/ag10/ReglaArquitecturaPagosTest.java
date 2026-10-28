package com.rutacolca.ag10;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Stream;

/**
 * Función de Aptitud Arquitectónica (Fitness Function) - AG-10 / Tema 10
 * Inspirado en 'Building Evolutionary Architectures' (Ford et al., 2022) y el ejemplo
 * ReglaDependencias.java de la Sesión Teórica 10 (slide 27).
 *
 * Regla Arquitectónica Evaluada:
 * "El paquete de Dominio (com.rutacolca.ag10.dominio) es el núcleo del negocio y
 * está estrictamente prohibido que importe clases de infraestructura, servicios
 * o resiliencia externa (Arquitectura Hexagonal / Puertos y Adaptadores)."
 */
public class ReglaArquitecturaPagosTest {

    private static final List<String> IMPORTS_PROHIBIDOS_EN_DOMINIO = List.of(
            "import com.rutacolca.ag10.servicio",
            "import com.rutacolca.ag10.resiliencia",
            "import java.sql",
            "import javax.sql",
            "import org.springframework"
    );

    public static void main(String[] args) throws IOException {
        System.out.println("================================================================================");
        System.out.println(" FUNCIÓN DE APTITUD ARQUITECTÓNICA (FITNESS FUNCTION) - AG-10");
        System.out.println(" Verificación de Regla de Independencia de Dominio (Hexagonal)");
        System.out.println("================================================================================\n");

        Path rutaDominio = Path.of("src/com/rutacolca/ag10/dominio");
        if (!Files.exists(rutaDominio)) {
            System.err.println("Directorio de dominio no encontrado: " + rutaDominio.toAbsolutePath());
            System.exit(1);
        }

        List<String> violaciones;
        try (Stream<Path> fuentes = Files.walk(rutaDominio)) {
            violaciones = fuentes.filter(p -> p.toString().endsWith(".java"))
                    .flatMap(ReglaArquitecturaPagosTest::buscarImportsProhibidos)
                    .toList();
        }

        if (!violaciones.isEmpty()) {
            System.err.println("¡ALERTA DE ARQUITECTURA! Se detectaron violaciones a la regla de diseño:");
            violaciones.forEach(v -> System.err.println("  ❌ " + v));
            System.exit(1);
        } else {
            System.out.println("✓ REGLA DE APTITUD CUMPLIDA:");
            System.out.println("  El paquete 'com.rutacolca.ag10.dominio' está 100% libre de acoplamiento a servicios o infraestructura.");
            System.out.println("  Se preserva la pureza arquitectónica requerida por la Arquitectura Hexagonal y el ADR-001.\n");
        }
    }

    private static Stream<String> buscarImportsProhibidos(Path archivo) {
        try {
            return Files.readAllLines(archivo).stream()
                    .map(String::trim)
                    .filter(linea -> IMPORTS_PROHIBIDOS_EN_DOMINIO.stream().anyMatch(linea::startsWith))
                    .map(linea -> archivo.getFileName() + " contiene violación: " + linea);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
